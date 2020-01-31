import json, csv, time
import requests
import ibm_boto3
from os.path import join, dirname
from json import JSONDecodeError

from bs4 import BeautifulSoup
from io import BytesIO
from tika import parser

# translate_selenium is a python file
from translate_selenium import Translate

from ibm_botocore.client import Config, ClientError
from ibm_watson import PersonalityInsightsV3, DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from settings import (
    PERSONALITY_INSIGHT_AUTHENTICATOR,
    PERSONALITY_INSIGHT_SERVICE_URL,
    DISCOVERY_AUTHENTICATOR,
    DISCOVERY_SERVICE_URL,
    COS_ENDPOINT,
    COS_API_KEY_ID,
    COS_AUTH_ENDPOINT,
    COS_RESOURCE_CRN,
    BUCKET_NAME
)

# export PYTHONPATH=/path/to/orm:$PYTHONPATH
# or SET PYTHONPATH=/path/to/orm:$PYTHONPATH
# Final alternative is copying the orm.py file in the same directory as this script.
from orm import get_analysis_data

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)\
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

# From translate selenium.
#translator = Translate(from_lang = 'id', to_lang = 'en')
counter = 0

# COS Instance
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT,
    ibm_service_instance_id=COS_RESOURCE_CRN, 
)

# Personality Insight Authenticator
authenticator = IAMAuthenticator(PERSONALITY_INSIGHT_AUTHENTICATOR)
personality_insights = PersonalityInsightsV3(
    version='2017-10-13',
    authenticator=authenticator
)
personality_insights.set_service_url(PERSONALITY_INSIGHT_SERVICE_URL)

# Discovery Authenticator
authenticator = IAMAuthenticator(DISCOVERY_AUTHENTICATOR)
DiscoveryService = DiscoveryV1(
    version='2019-11-22',
    authenticator=authenticator
)
DiscoveryService.set_service_url(DISCOVERY_SERVICE_URL)

def get_url_content(url):
    global counter

    headers = {
        'User-Agent': USER_AGENT
    }

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=20)

    session.mount('https://', adapter)
    session.mount('http://', adapter)

    # Get content from source. If fail, skip.
    try:
        content_request = session.get(url, headers=headers)
    except Exception as e:
        print("Error: ", e)
        print("Current news skipped!")
        return

    # Alternative Beautiful Soup - Get just the text.
    soup = BeautifulSoup(content_request.content, "html.parser")
    text = soup.find_all(text = True)
    output = ''
    blacklist = [
        	'[document]',
	        'noscript',
	        'header',
	        'html',
	        'meta',
	        'head', 
	        'input',
	        'script',
            'style',
            'footer'
    ]
    
    for characters in text:
        if characters.parent.name not in blacklist:
            output += '{}'.format(characters)

    # Remove newlines, tabspaces.
    output = output.replace("\t", "").replace("\r", "").replace("\n", "")
    print("Translating document number: ", counter)
    
    # Skip documents if more than 10 (lagging issues).
    if counter >= 10:
        print("Skip... more than 10 documents...")
        return
    
    output = translator.translate(output)
    counter += 1
    return output

def process_pdf_path(pdf_path):
    databytes = cos.Object(BUCKET_NAME, pdf_path).get()['Body'].read()
    buffer_data = BytesIO(databytes)
    content = parser.from_buffer(buffer_data)
    parsed = content['content'].replace("\n","")
    return parsed

def process_news_urls(urls_path):
    # Counter for document number.
    global counter
    counter = 0

    urls_path = urls_path.replace(" ","")
    print("Currently getting data from path {}".format(urls_path))
    cos_object = cos.Object(BUCKET_NAME, urls_path)
    file_content = cos_object.get()['Body'].read().decode('utf-8')

    urls = file_content.split("\n")
    # Remove empty string from list
    urls = list(filter(None, urls))
    contents = list(map(get_url_content, urls))
    return contents

def personality_insight_processor(personality_insights):
    data = get_analysis_data()
    i = 0

    # Convert to list for indexing.
    dataPDF = list(data.get('pdf_path'))
    company_name = list(data.get('name'))

    # Algorithm for analyzing.
    for content in dataPDF:
        text = process_pdf_path(content)
        response = personality_insights.profile(
            text,
            accept="text/csv",
            content_type='text/plain;charset=utf-8',
            consumption_preferences=True,
            csv_headers=False,
            raw_scores=True).get_result()
        profile = response.content
        print("Data number ", i+1, " processed! Inserting into CSV...\n\n")
        insert_to_csv(profile, company_name[i])
        i += 1

def insert_to_csv(profile, company_name):
    with open('output/resultsCSV.csv', 'a', newline='') as csvfile:
        cw = csv.writer(csvfile, delimiter=',')
        cr = csv.reader(profile.decode('utf-8').splitlines())
        my_list = list(cr)
        for row in my_list:
            row.insert(0, company_name)
            cw.writerow(row)
            print(row)

    # After writing to a CSV file, print this message.
    print("Written to CSV file successfully!")

# Inference / Analysis with Discoverys
def DiscoveryProcessor(DiscoveryService):
    kontenHasil = get_analysis_data()
    pathHasilNews = list(kontenHasil.get('news_urls_path'))

    # Change value here for starting from a certain index.
    # Add a pathHasilNews[x:] to start from a certain index. Index is x.
    # Example, starting from index 15 in Excel/CSV means 15 - 2 = 13, where 2 is a constant (minus header and starting from 0).
    for content in pathHasilNews:
        # Discovery Stuff
        # Add new env.
        response = DiscoveryService.create_environment(
            name="My Testing Environment",
            description="Latian"
        ).get_result()
        print(json.dumps(response, indent=2))

        hasil = json.dumps(response, indent = 2)
        kamus = json.loads(hasil)
            
        environmentID = kamus['environment_id']
        print(environmentID)

        # Add new config for keyword extraction
        with open('config.json', 'r') as config_data:
            data = json.load(config_data)
            new_config = DiscoveryService.create_configuration(
                environmentID,
                data['name'],
                description=data['description'],
                conversions=data['conversions'],
                enrichments=data['enrichments'],
                normalizations=data['normalizations']
            ).get_result()

        print(json.dumps(new_config, indent=2))

        # Get configuration id.
        configs = DiscoveryService.list_configurations(environmentID).get_result()
        print(json.dumps(configs, indent=2))
        hasil = json.dumps(configs, indent=2)
        kamus = json.loads(hasil)
        configurationID = kamus['configurations'][1]['configuration_id']
            
        # Set the configuration for keyword extraction.
        # Add new collection.
        new_collection = DiscoveryService.create_collection(
            environment_id = environmentID,
            configuration_id = configurationID,
            name = 'Hello World',
            description = 'Penampung sementara untuk analisa.',
            language = 'en'
        ).get_result()
        print(json.dumps(new_collection, indent=2))

        hasil = json.dumps(new_collection, indent = 2)
        kamus = json.loads(hasil)
        collectionID = kamus['collection_id']

        print("Processing data...")
        hasil = process_news_urls(content)

        for eachNews in hasil:
            # Extract to HTML.
            try:   
                for news in eachNews:
                    with open("test-case.html", "w", encoding='utf-8') as html_file:
                        html_file.write(eachNews)
                        html_file.close()
            except Exception as e:
                continue
            
            # Dump all the results into the Discovery.
            with open('test-case.html', 'r', encoding='utf-8') as html:
                add_doc = DiscoveryService.add_document(environmentID, collectionID, file = html).get_result()
            print(json.dumps(add_doc, indent=2))    

            print("Adding more documents of the same company.")    

        # After all the documents have been added, then query.
        print("Waiting for the documents to be processed...")
        time.sleep(15)
        print("Querying current documents....")
        queryandInsert(DiscoveryService, environmentID, collectionID)

        # Wait for the documents to be processed.
        print("Adding more documents of a different company... If this is the last, then ignore...")

def queryandInsert(DiscoveryService, environmentID, collectionID):
    # Query
    query_res = DiscoveryService.query(environmentID, collectionID).get_result()
    print(json.dumps(query_res, indent=2))
    hasil = json.dumps(query_res, indent=2)
    kamus = json.loads(hasil)

    # Get Sentiment
    numberofResults = kamus['matching_results']
    tempBarisStorage = []
    i = 0

    # Iterate through the dictionary and get all the sentiment.
    # Number of results should always be reduced by 1. Why? I don't know. This is a bug.
    # If you do not reduce by 1, then the array will always be out of bounds.
    # Update: Number of results should always be 10. This is a bug.
    while i < 10:
        try:
            tempBarisStorage.append(kamus['results'][i]['enriched_text']['sentiment']['document']['score'])
        except Exception as e:
            tempBarisStorage.append(0)
            i += 1
        else:
            print(tempBarisStorage[i])
            i += 1

    # Average Values
    j = 0
    baris = 0
    
    # Count the average values of the sentiment.
    while j < len(tempBarisStorage):
        baris = tempBarisStorage[j] + baris
        j += 1

    baris = baris / len(tempBarisStorage)

    with open('resultsDiscovery.csv', 'a', newline='\n') as csvfile:
        temp = []
        temp.append(baris)

        tulisCSV = csv.writer(csvfile, delimiter=',')
        tulisCSV.writerow(temp)

    # Remove collection.
    delete_collection = DiscoveryService.delete_collection(environmentID, collectionID).get_result()
    print(json.dumps(delete_collection, indent=2))

    # Delete env.
    del_env = DiscoveryService.delete_environment(environmentID).get_result()
    print(json.dumps(del_env, indent=2))

# Main Function
def main():
    # PersonalityInsightProcessor(personality_insights)
    personality_insight_processor(personality_insights)
    # DiscoveryProcessor(DiscoveryService)

if __name__ == "__main__":
    main()
