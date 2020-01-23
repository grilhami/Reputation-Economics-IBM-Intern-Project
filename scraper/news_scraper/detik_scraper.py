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

FIRST_YEAR = 2017
SECOND_YEAR = 2018
KEYWORD = "tenaga nuklir indonesia"

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT,
    ibm_service_instance_id=COS_RESOURCE_CRN,
            
)

class DetikScraper(scrapy.Spider):
    name = "detik_scraper"
    allowed_domains = ["www.detik.com"]
    start_urls = ["https://www.detik.com/"]

    def __init__(self, keyword='', *args,**kwargs):
        super(DetikScraper, self).__init__(*args, **kwargs)
        self.keyword = keyword
        options = Options()
        options.headless = True
        chromedriver_path = "/mnt/c/Users/Gilang R Ilhami/Desktop/personal_projects/ibm_stuff/chromedriver.exe"
        # self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)

        # Commend code above, and 
        # uncomment code below
        # to remove headless scraping.
        self.driver = webdriver.Chrome(executable_path=chromedriver_path)

    def parse(self, response):

        url = response.url
        self.driver.get(url)
        self.driver.implicitly_wait(20)

        self.driver.implicitly_wait(10)
        input_search = self.driver.find_element_by_xpath("//*[@id='search_navbar']/input[1]")
        input_search.send_keys(self.keyword.lower())
        input_search.send_keys(Keys.RETURN)

        self.driver.implicitly_wait(10)
        news_list = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[2]")

        link_list = news_list.find_elements_by_tag_name("a")
        
        link_not_none = lambda link: link.get_attribute("href") is not None
        link_list = [link.get_attribute("href") for link in link_list if link_not_none]

        # index of last elemtn in link_list
        last_idx = -1

        print("="*20)
        print("GETTING LAST INDEX")
        print("="*20)

        # Get the latest year from the latest news
        for _ in range(len(link_list)):

            try:
                latest_news_year = retrieve_date_year(link_list[last_idx], "div", "class", "date")
                print(f"Found latest year at index {last_idx}")
                print(f"Latest year is {latest_news_year}")
                break
            except:

                try:
                    latest_news_year = retrieve_date_year(link_list[last_idx], "div", "class", "detail__date")
                    print(f"Found latest year at index {last_idx}")
                    print(f"Latest year is {latest_news_year}")
                    break
                except Exception as e:
                    print(f"Can't find latest year with index {last_idx}: '{e}'")

            last_idx -= 1

        
        if latest_news_year < FIRST_YEAR:
            all_links = link_list
        else:
            all_links = []

        # While the latest news larger than
        # the first year, retrieve the url.
        while latest_news_year >= FIRST_YEAR:

            print("="*20)
            print("Retrieving all the news url...")
            print("="*20)
            # Wait to load page
            time.sleep(5)

            self.driver.implicitly_wait(10)
            news_list = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[2]")

            link_list = news_list.find_elements_by_tag_name("a")

            link_not_none = lambda link: link.get_attribute("href") is not None
            link_list = [link.get_attribute("href") for link in link_list if link_not_none]

            all_links.extend(link_list)

            last_idx = -1

            for _ in range(len(link_list)):
                try:
                    latest_news_year = retrieve_date_year(link_list[last_idx], "div", "class", "date")
                    print(f"Found latest year at index {last_idx}")
                    print(f"Latest year is {latest_news_year}")
                    break
                except:
                    try:
                        lastest_news_year = retrieve_date_year(link_list[last_idx], "div", "class", "detail__date")
                        print(f"Found latest year at index {last_idx}")
                        print(f"Latest year is {latest_news_year}")
                        break
                    except Exception as e:
                        print(f"Can't find latest year with index {last_idx}: '{e}'")
                last_idx -= 1
            
            try:

                pages = self.driver.find_element_by_tag_name("div[class*='paging text_center']")
                current_page = pages.find_element_by_tag_name("a[class*='selected']")
                current_page_num = int(current_page.text)
                current_page_link = current_page.get_attribute("href")

            except Exception as e:

                print("Something went wrong while going to next page.")
                print(e)
                
                print("Going back")
                self.driver.execute_script("window.history.go(-1)")
                
                print("Skipping next page")
                next_next_page = current_page_num + 2
                next_next_link = current_page_link[:-1] + str(next_next_page)
                self.driver.get(next_next_link)

            else:

                next_page = pages.find_elements_by_tag_name("a")[-1]
                next_page.click()

        links = all_links.copy()

        first_year_contents = []
        second_year_contents = []

        all_index = set(map(links.index, links))

        error_dates_index = set()

        for link in links:
            try:
                date = retrieve_date_year(link,"div", "class", "date")
            except:
                try:
                    date = retrieve_date_year(link,"div", "class", "detail__date")
                except Exception as e:
                    print(f"Cannot get content from {link}. {e}\n\n")
                    error_idx = links.index(link)
                    error_dates_index.add(error_idx)
        
        can_get_dates_index = list(all_index - error_dates_index)

        current_date = datetime.datetime.now()
        current_year = current_date.year

        for content_index in can_get_dates_index:

            # News Publish Date
            try:
                content_date = retrieve_date_year(links[content_index],"div", "class", "date")
            except:
                try:
                    content_date = retrieve_date_year(links[content_index],"div", "class", "detail__date")
                except:
                    print(f"{link[content_index]} cannot be scraped.")

            print(content_date)

            # Seperating First Year and Second Year contents
            if content_date >= FIRST_YEAR and content_date < SECOND_YEAR:
                first_year_contents.append(links[content_index])
            elif content_date >= SECOND_YEAR and content_date < current_year:
                second_year_contents.append(links[content_index])
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

def detik(company_names):

    if not isinstance(company_names, list):
        raise ValueError(f"company_names must be list, found {type(company_names)} instead.")

    first_year_paths = [] 
    second_year_paths = []

    process = CrawlerProcess()
    for company_name in company_names:
        company_name = company_name.replace("_"," ")
        process.crawl(DetikScraper, keyword=company_name)

        dirname = f"assets/{company_name}/news_urls/"

        filename_first_year = dirname + f"{company_name}_detik_{FIRST_YEAR}.txt"
        first_year_paths.append(filename_first_year)

        filename_second_year = dirname + f"{company_name}_detik_{SECOND_YEAR}.txt"
        second_year_paths.append(filename_second_year)

    process.start()

    dirname = f"assets/{company_name}/news_urls/"

    return first_year_paths, second_year_paths
