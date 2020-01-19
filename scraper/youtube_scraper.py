import os
import re
import ibm_boto3

from datetime import datetime
from pytube import YouTube
from ibm_botocore.client import Config, ClientError

from settings import (
    COS_ENDPOINT,
    COS_API_KEY_ID,
    COS_AUTH_ENDPOINT,
    COS_RESOURCE_CRN 
)

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT,
    ibm_service_instance_id=COS_RESOURCE_CRN,
            
)

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def clean_string(s):
    s = cleanhtml(s)
    s = re.sub("\n", "", s)
    s = re.sub("-->", "", s)
    s = re.sub('[^\w\s]','',s)
    s = re.sub("\d+", "", s)
    return s

def youtube_captions(url):
    
    if (url is None) or (url == ""):
        return ""

    source = YouTube(url)
    
    caption = source.captions.get_by_language_code('en')
    
    if caption is None:
        caption = source.captions.get_by_language_code('id')

    caption_convert_to_srt =(caption.generate_srt_captions())
    
    final_text = " ".join(clean_string(caption_convert_to_srt).split())
    title = source.title

    return final_text, title

def youtube_scraper(url, company):
    
    company = company.replace(" ", "_")
    
    # Create path for original and parsed pdf
    BASE_URL = "assets/"
    link_path = BASE_URL + f"{company}/youtube/"

    
    if not os.path.exists(link_path):
        os.makedirs(link_path)
        
    if url == "":
        return None
    
    captions, title = youtube_captions(url)
    saved_date = datetime.now().strftime("%d-%m-%Y")
    filename = re.sub("[^a-zA-Z0-9]+", "_", title.lower())
    file_path = link_path + filename + ".txt"
    
    bucket_name = "cos-standard-7ry"

    cos.Object(bucket_name, file_path).put(Body=captions)
        
    return file_path