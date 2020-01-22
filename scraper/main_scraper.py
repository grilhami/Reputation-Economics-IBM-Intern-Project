import argparse
import ibm_boto3
import pandas as pd

from ibm_botocore.client import Config, ClientError
from numpy import nan
from datetime import datetime

from pdf_scraper import pdf_scraper
from youtube_scraper import youtube_scraper
from news_scraper.detik_scraper import detik
from news_scraper.liputanenam_scraper import liputanenam

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
    

    return df


def run_scraper(path):
    
    path_extension = path.split(".")[-1]
    
    if path_extension != "xlsx":
        raise ValueError("expected file with xlsx extension, but found '{}' instead.".format(path_extension))


    try:
        df = pd.read_excel(path)
        company_df = process_excel(df)
    except Exception as e:
        raise ValueError(e)

    if "company_name" not in company_df.columns:
        raise KeyError("column name 'comapny_name' is not found in excel file.")
    else:
        companies = company_df['company_name'].values.tolist()

    #import ipdb; ipdb.set_trace()
    pdf_urls = company_df['link'].values.tolist()
    youtube_urls = company_df['youtube_link'].values.tolist()

    page_ranges = list(map(get_range, df['page'].values.tolist()))

    data_dict = {
        'company_name': [],
        'path_to_pdf_file':[],
        'path_to_youtube_transcript': [],
        'path_to_news_urls': [],
        'stored_date': []
    }


    for company_i in range(len(companies)):
        print(f"Fetching data on {companies[company_i]}...\n\n")
        print("Retrieving PDF file.")

        # TODO: pdf_scraper result in the
        # following error:
        # http.client.IncompleteRead: IncompleteRead(1108131 bytes read, 7408904 more expected)
        # Need to be fixed, check:
        # https://stackoverflow.com/questions/51226635/http-client-incompleteread-error-in-python3

        path_to_pdf_file = pdf_scraper(
                                        cos,
                                        pdf_urls[company_i],
                                        companies[company_i],
                                        page_ranges[company_i],
                                        mode='parsed'
                                        )

        if isinstance(youtube_urls[company_i], str):
            print("Retrieving Youtube Transcript file.")
            try:
                path_to_youtube_transcript = youtube_scraper(
                                                            cos,
                                                            companies[company_i],
                                                            youtube_urls[company_i]
                                                            )
            except Exception as e:
                print(f"Cannot access the link{companies[company_i]}, because {e}.")
                path_to_youtube_transcript = ""

        else:
            print(f"{companies[company_i]} does not have a youtube link.")
            path_to_youtube_transcript = ""

        liputanenam_path = liputanenam(companies[company_i])
        detik_path = detik(companies[company_i])
        urls_path = liputanenam_path[1] + detik_path[1]

        stored_date = datetime.now()

        data_dict['company_name'].append(companies[company_i])
        data_dict['path_to_pdf_file'].append(path_to_pdf_file)
        data_dict['path_to_youtube_transcript'].append(path_to_youtube_transcript)
        data_dict['path_to_news_urls'].append(urls_path)
        deta_dict['stored_date'].append(stored_date)
        
    return data_dict

if __name__ == "__main__":

    data = run_scraper(PATH)

    df = pd.DataFrame.from_dict(data)

    print(df)
