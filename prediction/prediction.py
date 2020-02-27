import argparse
import json
import tempfile
import requests

from bs4 import BeautifulSoup
from configparser import ConfigParser
from io import BytesIO
from tika import parser as pdf_parser

from translate_selenium import Translate

from ibm_botocore.client import Config, ClientError
from ibm_watson import PersonalityInsightsV3, DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from watson_machine_learning_client import WatsonMachineLearningAPIClient

config = ConfigParser()
config.read("prediction.conf")

parser = argparse.ArgumentParser(description='Provide required files for prediction.')
parser.add_argument('--path-cxo-pdf-file', type=str,
                    help="path to the pdf file that contains CXO's statement (e.g. annual report)")
parser.add_argument('--path-news-list', type=str,
                    help='path to txt file that contains list of news')
parser.add_argument('--company-profitability', type=float,
                    help="Profitability of a company from annual report.")
parser.add_argument('--company-to-query', type=str,
                    help="Company name to be queried.")

args = parser.parse_args()

PATH_TO_CXO_STATEMENT = args.path_cxo_pdf_file
PATH_TO_NEWS_LSIT = args.path_news_list
PROFITABILITY = args.company_profitability
COMPANY_NAME = args.company_to_query

# IBM Credentials
WML_CREDENTIALS = {
  "url": config['watson-machine-learning']['url'],
  "apikey": config['watson-machine-learning']['apikey'],
  "instance_id": config['watson-machine-learning']['instance_id']
}

WML_ENDPOINT = config['watson-machine-learning']['endpoint']

PERSONALITY_INSIGHT_AUTHENTICATOR = config['personality-insight']['apikey']
PERSONALITY_INSIGHT_SERVICE_URL = config['personality-insight']['url']
DISCOVERY_AUTHENTICATOR = config['discovery']['apikey']
DISCOVERY_SERVICE_URL = config['discovery']['url']

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)\
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

# Personality Insight Authenticator
authenticator = IAMAuthenticator(PERSONALITY_INSIGHT_AUTHENTICATOR)
personality_insights = PersonalityInsightsV3(
    version='2017-10-13',
    authenticator=authenticator
)
personality_insights.set_service_url(PERSONALITY_INSIGHT_SERVICE_URL)

# Discovery Authenticator
authenticator = IAMAuthenticator(DISCOVERY_AUTHENTICATOR)
discovery = DiscoveryV1(
    version='2019-11-22',
    authenticator=authenticator
)
discovery.set_service_url(DISCOVERY_SERVICE_URL)

# Watson Machine Learning Client
client = WatsonMachineLearningAPIClient(WML_CREDENTIALS)

def get_self_expresion(filepath):
    
    content = pdf_parser.from_file(filepath)['content']
    profile = personality_insights.profile(
            content,
            accept="application/json",
            content_type='text/plain;charset=utf-8',
            consumption_preferences=False,
            raw_scores=False).get_result()

    needs = profile['needs']
    needs_percentile = lambda x: True if needs[x]['trait_id'] == 'need_self_expression' else False

    percentile, = [needs[i]['percentile'] for i in range(len(needs)) if needs_percentile(i)]

    return percentile

def get_news_content(url):
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
        print(f"Something went wrong when retrieving content from {url}: {e}")
        return

    soup = BeautifulSoup(content_request.content, "html.parser")
    text = soup.prettify()

    # TODO: Integrate translator
    return text

def get_environment_id():
    environments = discovery.list_environments().get_result()['environments']

    assert len(environments) != 0, "Sytem Environment nor detected."

    if len(environments) > 1:
        environment_id = environments[1]['environment_id']
        return environment_id
    else:
        discovery.create_environment(
                                    name="my_environment",
                                    description="My environment"
                                ).get_result()
        environments= discovery.list_environments().get_result()

        environment_id = environments['environments'][1]['environment_id']
        return environment_id
    
def get_config_id():
    environment_id = get_environment_id()

    configs = discovery.list_configurations(environment_id).get_result()['configurations']

    with open('discovery_config.json', 'r') as config_data:
        data = json.load(config_data)

        if len(configs) != 0:

            right_name = lambda x: True if configs[x]['name'] == data['name'] else False

            config_id, = [configs[i]['configuration_id'] for i in range(len(configs)) if right_name(i)]
            return config_id
        else:
            
            new_config = discovery.create_configuration(
                environment_id,
                data['name'],
                description=data['description'],
                conversions=data['conversions'],
                enrichments=data['enrichments'],
                normalizations=data['normalizations']
            ).get_result()

            configs = discovery.list_configurations(environment_id).get_result()
            config_id = configs['configurations'][0]['configuration_id']
            return config_id

def get_collection_id():
    environment_id = get_environment_id()
    config_id = get_config_id()

    collections = discovery.list_collections(environment_id).get_result()['collections']

    # Check if collection already created

    collection_names = [collection['name'] for collection in collections]

    if 'Company CXO Reputation' not in collection_names:
        discovery.create_collection(environment_id=environment_id,
                                    configuration_id=config_id, 
                                    name="Company CXO Reputation", 
                                    description="News Collections",
                                    language='en').get_result()

    if len(collections) != 0:
        #import ipdb;ipdb.set_trace()
        right_name = lambda x: True if collections[x]['name'] == 'Company CXO Reputation' else False
        collection_id, = [collections[i]['collection_id'] for i in range(len(collections)) if right_name(i)]
        return collection_id
    else:
        new_collection = discovery.create_collection(
                                                    environment_id=environment_id,
                                                    configuration_id=config_id, 
                                                    name="Company CXO Reputation", 
                                                    description="News Collections",
                                                    language='en').get_result()
        collection_id = new_collection['collection_id']
        return collection_id

def reset_collection(current_collection_id):
    environment_id = get_environment_id()
    config_id = get_config_id()

    discovery.delete_collection(
                                environment_id, 
                                current_collection_id).get_result()
    new_collection = discovery.create_collection(
                                                environment_id=environment_id,
                                                configuration_id=config_id, 
                                                name="Company CXO Reputation", 
                                                description="News Collections",
                                                language='en').get_result()
    collection_id = new_collection['collection_id']
    return collection_id


def processs_news_urls(filepath):
    for url in open(filepath, "r"):

        try:
            content = get_news_content(url.replace("\n", ""))
        except Exception as e:
            print(f"Something went wrong processing {url}")
        finally:
            yield content


        yield get_news_content(url.replace("\n", ""))

def get_overall_sentiment(filepath, company_name, collection_reset=True):
    environment_id = get_environment_id()
    collection_id = get_collection_id()

    if collection_reset:
        collection_id = reset_collection(collection_id)
    
    with open(filepath, "r") as f:
        news_urls = f.read().split("\n")
    
    # Generator for content
    news_contents = processs_news_urls(filepath)

    for _ in range(len(news_urls)):

        try:
            content = next(news_contents)
        except StopIteration:
            break

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.name = temp_file.name + ".html"
            temp_file.write(str.encode(content))
            temp_file.seek(0)
            discovery.add_document(environment_id,
                                    collection_id, 
                                    file =temp_file).get_result()
    
    query_result = discovery.query(environment_id, 
                                    collection_id, 
                                    query=company_name).get_result()

    results = query_result['results']

    sentiment_scores = [results[i]['enriched_text']['sentiment']['document']['score'] \
                        for i in range(len(results))]

    overall_sentiment = sum(sentiment_scores)/len(sentiment_scores)
    return overall_sentiment

def prediction(overall_sentiment, need_self_expression, profitability):
    fields = ['overall_sentiment', 'need_self_expression', 'profitability_2018']
    values = [overall_sentiment, need_self_expression, profitability]
    scoring_payload = {"fields": fields, "values":[values]}
    predictions = client.deployments.score(WML_ENDPOINT, scoring_payload)
    return predictions

def main():
    need_self_expression = get_self_expresion(PATH_TO_CXO_STATEMENT)
    overall_sentiment = get_overall_sentiment(PATH_TO_NEWS_LSIT, COMPANY_NAME)
    profitability = PROFITABILITY

    prediction_result = prediction(overall_sentiment, need_self_expression, profitability)
    print(prediction_result)

if __name__ == "__main__":
    main()

    