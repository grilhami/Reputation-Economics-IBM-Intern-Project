import requests
import dateutil.parser
import datetime
import time

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from urllib.parse import urlparse


####################################
######## NEWS SCRAPER UTILS ########
####################################

MONTH_DICT = {'Januari': 'January',
            'Februari': 'February',
            'Maret': 'March',
            'April': 'April',
            'Mei': 'May',
            'Juni': 'June',
            'Juli': 'July',  
            'Agustus': 'August',
            'September': 'September',
            'Oktober': 'October',
            'November': 'November',
            'Desember': 'December'
            }

MONTH_ACR_DICT = {'Jan': 'Jan',
                'Feb': 'Feb',
                'Mar': 'Mar',
                'Apr': 'Apr',
                'Mei': 'May',
                'Jun': 'Jun',
                'Jul': 'Jul',
                'Agu': 'Aug',
                'Sep': 'Sep',
                'Okt': 'Oct',
                'Nov': 'Nov',
                'Des': 'Dec'
                }

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)\
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
     
MAX_RETRIES = 20

def retrieve_date_year(url, html_tag, attribute, attribute_value):
    """
        Retrieve year from dates of content
    """
    
    assert isinstance(url, str), f"Argument required str, but a {type(url)} was given."
    
    headers = {
        'User-Agent': USER_AGENT
    }

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
    
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    
    # Get content from source
    content_request = session.get(url, headers=headers)

    soup = BeautifulSoup(content_request.content)
    
    date_text = soup.find(
        html_tag, 
        {attribute: attribute_value}
    ).text
    
    # Parsed date if month is not acronym
    for month in MONTH_DICT.keys():
        if month in date_text:
            date_text = date_text.replace(month, MONTH_DICT[month])
        else:
            pass
    # Parsed date if month is an acronym
    for month in MONTH_ACR_DICT.keys():

        if month in date_text:
            date_text = date_text.replace(month, MONTH_ACR_DICT[month])
        else:
            pass
    
    date_year = dateutil.parser.parse(date_text, fuzzy=True).year

    return date_year

####################################
######## PDF SCRAPER UTILS ########
####################################

def datetime_to_str(date):
    if isinstance(date, datetime):
        return date.strftime("%m-%d")
    else:
        return date

def get_range(range_str):
    """
        Get page range from the 'Page' column
    """
    if isinstance(range_str, datetime):
        range_str = datetime_to_str(range_str)
    if "-" in range_str:
        nums = range_str.split("-")
        return (int(nums[0]), int(nums[1]))
    else:
        nums = range_str.split("to")
        return (int(nums[0]), int(nums[1]))



####################################
###### YOUTUBE SCRAPER UTILS ######
####################################

def youtube_links(links):
    links = links.split(",")
    
    if len(links) == 1:
        return ""
    else:
        return links[1]