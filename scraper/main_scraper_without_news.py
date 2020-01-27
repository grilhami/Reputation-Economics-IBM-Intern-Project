import os
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


# Need to run:
# export PYTHONPATH=/path/to/orm:$PYTHONPATH
from orm import insert_to_db

from settings import (
    COS_ENDPOINT,
    COS_API_KEY_ID,
    COS_AUTH_ENDPOINT,
    COS_RESOURCE_CRN,
    BUCKET_NAME
)

from utils import (
    youtube_links,
    get_range,
    datetime_to_str
)

ap = argparse.ArgumentParser()
ap.add_argument("--excel-path", required=True, help="Path to the excel file that contains the company list.")
ap.add_argument("--news-urls-folder", required=True, help="Path to the folder containing news urls for each company")

args = vars(ap.parse_args())

PATH = args['excel_path']
NEWS_URLS_FOLDER = args['news_urls_folder']

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

def process_news_folder(folder_path):
    
    if not os.path.exists(folder_path):
        raise ValueError("Folder does not exist.")

    urls_files = os.listdir(folder_path)

    data_dict = {}

    for urls_file in urls_files:
        company_name = urls_file.replace("_detik_2018.txt","").replace("_", " ")
        data_dict[company_name] = urls_file
    return data_dict


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
        """
            SCRAPE COMPANY DATA USING INDEX
        """
        # Changed value here
        companies = company_df['company_name'].values.tolist()

    cxos = company_df['cxo'].values.tolist()

    pdf_urls = company_df['link'].values.tolist()
    youtube_urls = company_df['youtube_link'].values.tolist()

    page_ranges = list(map(get_range, df['page'].values.tolist()))

    company_names_dict = process_news_folder(NEWS_URLS_FOLDER)


    data_dict = {
        'company_name': [],
        'cxo_name': [],
        'path_to_pdf_file':[],
        'pdf_stored_date': [],
        'path_to_youtube_transcript': [],
        'youtube_stored_date':[],
        'news_urls_stored_date': [],
        'path_to_news_urls': []
    }


    for company_i in range(len(companies)):
        print(f"Fetching data on {companies[company_i]}...\n\n")
        print("Retrieving PDF file.")

        data_dict['company_name'].append(companies[company_i])
        data_dict['cxo_name'].append(cxos[company_i])


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

        pdf_stored_date = datetime.now().strftime("%Y-%m-%d")
        data_dict['path_to_pdf_file'].append(path_to_pdf_file)
        data_dict['pdf_stored_date'].append(pdf_stored_date)

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

        youtube_stored_date = datetime.now().strftime("%Y-%m-%d")

        data_dict['path_to_youtube_transcript'].append(path_to_youtube_transcript)
        data_dict['youtube_stored_date'].append(youtube_stored_date)

        print(f"Getting list of news urls related to {companies[company_i]}")
        try:
            urls_file_path = NEWS_URLS_FOLDER + company_names_dict[companies[company_i]]
            with open(urls_file_path, "r") as f:
                urls = f.read()
        except Exception as e:
            print(f"Could not retrieve company news urls because: {e}")
        else:
            print("Urls Fetched.")

        print("Storing urls to the IBM COS...")
        company_path = companies[company_i].replace(" ", "_")
        filename_ibm_cos = f"assets/{company_path}/news_urls/" + company_names_dict[companies[company_i]]

        cos.Object(BUCKET_NAME, filename_ibm_cos).put(Body=urls)
        data_dict['path_to_news_urls'].append(filename_ibm_cos)

        urls_stored_date = datetime.now()
        data_dict['news_urls_stored_date'].append(urls_stored_date.strftime("%Y-%m-%d"))
        print("URLS STORED.")
        
    return data_dict

if __name__ == "__main__":

    data = run_scraper(PATH)
    print(data)

    df = pd.DataFrame.from_dict(data)

    for i in range(len(df)):
        input_data = df.iloc[i].values.tolist()
        insert_to_db(
            company_name=input_data[0],
            cxo_name=input_data[1],
            path_to_parsed_pdf=input_data[2],
            path_to_youtube_transcript=input_data[4],
            links=input_data[7],
            pdf_stored_date=input_data[3],
            youtube_stored_date=input_data[5],
            news_urls_stored_date=input_data[6]
        )

    df.to_csv("../sample_files/sample.csv", index=False)

    print(df)
