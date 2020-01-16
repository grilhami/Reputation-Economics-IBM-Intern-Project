import scrapy
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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

