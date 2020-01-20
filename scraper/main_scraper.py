import argparse
import ibm_boto3
import pandas as pd

from ibm_botocore.client import Config, ClientError
from pdf_scraper import pdf_scraper
from youtube_scraper import youtube_scraper

from settings import (
    COS_ENDPOINT,
    COS_API_KEY_ID,
    COS_AUTH_ENDPOINT,
    COS_RESOURCE_CRN 
)

from utils import (
    youtube_links,
    get_range,
    datetime_to_str
)

ap = argparse.ArgumentParser()
ap.add_argument("--path_to_excel", required=True, help="Path to the excel file that contains the company list.")

args = vars(ap.parse_args())

PATH = args['path_to_excel']

# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT,
    ibm_service_instance_id=COS_RESOURCE_CRN,
            
)

def process_excel(df):

    columns = df.columns

    fix_columns = lambda x: x.lower().replace(" ", "_")
    
    new_column_names = list(map(fix_columns, columns))
    df.columns = new_column_names

    df = df[df['cxo'].notnull()]

    fix_companies = lambda x: x.lower().replace(" tbk.", "").replace(" (persero)","").replace("."," _")
    df['company_name'] = df['company_name'].apply(fix_companies)

    df['youtube_link'] = df['link'].apply(youtube_links)

    # TODO: Complete process excel (baseline on Scraper Baseline jupyter notebook)




def run_scraper(path):
    
    path_extension = path.split(".")[-1]
    
    if path_extension != "xlsx":
        raise ValueError("expected file with xlsx extension, but found '{}' instead.".format(path_extension))

    try:
        company_df = pd.read_excel(path)
    except Exception as e:
        raise ValueError(e)

    if "company_name" not in company_df.columns:
        raise KeyError("column name 'comapny_name' is not found in excel file.")
    else:
        companies = company_df['company_name'].values.tolist()

    pdf_urls = company_df['company_name'].values.tolist()
    youtube_urls = company_df['company_name'].values.tolist()
    

    return companies

if __name__ == "__main__":

    companies = run_scraper(PATH)

    print(companies)



print(PATH)