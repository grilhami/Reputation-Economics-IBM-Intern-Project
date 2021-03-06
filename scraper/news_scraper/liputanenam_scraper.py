import scrapy
import time
import datetime
import ibm_boto3

from ibm_botocore.client import Config, ClientError

from scrapy.crawler import CrawlerProcess

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from utils import retrieve_date_year

from settings import (
    COS_ENDPOINT,
    COS_API_KEY_ID,
    COS_AUTH_ENDPOINT,
    COS_RESOURCE_CRN,
    BUCKET_NAME
)

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT,
    ibm_service_instance_id=COS_RESOURCE_CRN,
            
)

FIRST_YEAR = 2017
SECOND_YEAR = 2018
KEYWORD = "tenaga nuklir indonesia"

class LiputanEnamScraper(scrapy.Spider):
    name = "liputanenam_scraper"
    allowed_domains = ["www.liputan6.com"]
    start_urls = ["https://www.liputan6.com/"]

    def __init__(self, keyword='', *args,**kwargs):
        super(LiputanEnamScraper, self).__init__(*args, **kwargs)
        self.keyword = keyword
        options = Options()
        options.headless = True
        chromedriver_path = "/mnt/c/Users/Gilang R Ilhami/Desktop/personal_projects/ibm_stuff/chromedriver.exe"
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)

        # Commend code above, and 
        # uncomment code below
        # to remove headless scraping.
        # self.driver = webdriver.Chrome(executable_path=chromedriver_path)

    def parse(self, response):
        url = response.url
        self.driver.get(url)
        self.driver.implicitly_wait(20)
        
        self.driver.implicitly_wait(10)
        input_search = self.driver.find_element_by_xpath("//*[@id='q']")
        input_search.send_keys(self.keyword.lower())
        input_search.send_keys(Keys.RETURN)
        
        self.driver.implicitly_wait(10)
        news_list = self.driver.find_element_by_xpath("//*[@id='main']/div[3]/div/article/div/section")
        link_list = news_list.find_elements_by_tag_name("h4")
        link_list = [title.find_element_by_tag_name("a") for title in link_list]
        link_list = [link.get_attribute("href") for link in link_list if link.get_attribute("href") is not None]
        
        if bool(link_list) is False:
            return None
        
        last_idx = -1
        for _ in range(len(link_list)):
            print("Last Index", last_idx)
            try:
                last_news_year = retrieve_date_year(link_list[last_idx], "time", "class", "read-page--header--author__datetime updated")
                break
            except Exception as e:
                print(e)
            last_idx -= 1
            
        
        page_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        
        # Sroll to the desired number of contents
        while last_news_year >= FIRST_YEAR:
            print("Scrolling down")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(5)
                
            self.driver.implicitly_wait(10)
            news_list = self.driver.find_element_by_xpath("//*[@id='main']/div[3]/div/article/div/section")

            link_list = news_list.find_elements_by_tag_name("h4")
            link_list = [title.find_element_by_tag_name("a") for title in link_list]

            link_not_none = lambda link: link.get_attribute("href") is not None
            link_list = [link.get_attribute("href") for link in link_list if link_not_none]
            
            last_idx = -1
            
            for _ in range(len(link_list)):
                try:
                    last_news_year = retrieve_date_year(
                        link_list[last_idx],
                        "time", 
                        "class", 
                        "read-page--header--author__datetime updated"
                        )
                    break
                except:
                    pass
                last_idx -= 1
                
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == page_height:
                break
            page_height = new_height


        self.driver.implicitly_wait(10)
        news_list = self.driver.find_element_by_xpath("//*[@id='main']/div[3]/div/article/div/section")

        link_list = news_list.find_elements_by_tag_name("h4")
        link_list = [title.find_element_by_tag_name("a") for title in link_list]

        link_not_none = lambda link: link.get_attribute("href") is not None
        link_list = [link.get_attribute("href") for link in link_list if link_not_none]
            
        first_year_contents = []
        second_year_contents = []
        
        all_index = set(map(link_list.index, link_list))
        
        error_dates_index = set()
        
        for link in link_list:
            try:
                date = retrieve_date_year(link,"time", "class", "read-page--header--author__datetime updated")
            except Exception as e:
                print(link)
                print(e, end="\n\n")
                error_idx = link_list.index(link)
                error_dates_index.add(error_idx)
                
        can_get_dates_index = list(all_index - error_dates_index)
        
        current_date = datetime.datetime.now()
        current_year = current_date.year
        
        for content_index in can_get_dates_index:
            
            # News Publish Date
            content_date = retrieve_date_year(link_list[content_index],"time", "class", "read-page--header--author__datetime updated")
            print(content_date)
            
            # First year news
            if content_date >= FIRST_YEAR and content_date < SECOND_YEAR:
                first_year_contents.append(link_list[content_index])
            elif content_date >= SECOND_YEAR and content_date < current_year:
                second_year_contents.append(link_list[content_index])
            else:
                pass

        self.driver.close()

        dirname = f"assets/{self.keyword}/news_urls/"
        filename_first_year = dirname + f"{self.keyword}_liputanenam_{FIRST_YEAR}.txt"
        filename_second_year = dirname + f"{self.keyword}_liputanenam_{SECOND_YEAR}.txt"

        if not first_year_contents:
            first_year_urls = "\n".join(first_year_contents)
        else:
            first_year_urls = ""

        if not second_year_contents:
            second_year_urls = "\n".join(second_year_contents)
        else:
            second_year_urls = ""
        
        cos.Object(BUCKET_NAME, filename_first_year).put(Body=first_year_urls)
        cos.Object(BUCKET_NAME, filename_second_year).put(Body=second_year_urls)

                
        yield {
            f"{FIRST_YEAR} contents":first_year_contents,
            f"{SECOND_YEAR} contents": second_year_contents

        }

def liputanenam(company_names):

    if not isinstance(company_names, list):
        raise ValueError(f"company_names must be list, found {type(company_names)} instead.")

    first_year_paths = [] 
    second_year_paths = []

    process = CrawlerProcess()
    for company_name in company_names:
        company_name = company_name.replace("_"," ")
        process.crawl(LiputanEnamScraper, keyword=company_name)

        dirname = f"assets/{company_name}/news_urls/"

        filename_first_year = dirname + f"{company_name}_liputanenam_{FIRST_YEAR}.txt"
        first_year_paths.append(filename_first_year)

        filename_second_year = dirname + f"{company_name}_liputanenam_{SECOND_YEAR}.txt"
        second_year_paths.append(filename_second_year)

    process.start()

    dirname = f"assets/{company_name}/news_urls/"

    return first_year_paths, second_year_paths