import scrapy
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from .utils import retrieve_date_year

FIRST_YEAR = 2017
SECOND_YEAR = 2018

class DetikScraper(scrapy.Spider):
    name = "detik_scraper"
    allowed_domains = ["www.detil.com"]
    start_urls = ["https://www.detik.com/"]

    def __init__(self):
        chromedriver_path = "/mnt/c/Users/Gilang R Ilhami/Desktop/personal_projects/ibm_stuff/chromedriver.exe"
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)

        # Commend code above, and 
        # uncomment code below
        # to remove headless scraping.
        # driver = webdriver.Chrome(executable_path=chromedriver_path)

    def parse(self, response):

        url = reponse.url
        self.driver.get(url)
        self.driver.implicitly_wait(20)

        self.driver.implicitly_wait(10)
        input_search = self.driver.find_element_by_xpath("//*[@id='search_navbar']/input[1]")
        input_search.send_keys(keyword.lower())
        input_search.send_keys(Keys.RETURN)

        driver.implicitly_wait(10)
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
                last_news_year = retrieve_date_year(link_list[last_idx], "div", "class", "date")
                print(f"Found latest year at index {last_idx}")
                print(f"Latest year is {last_news_year}")
                break
            except Exception as e:
                print(f"Can't find latest year with index {last_idx}")
            last_idx -= 1

        
        if last_news_year < FIRST_YEAR:
            all_link_list = link_list
        else:
            all_link_list = []

