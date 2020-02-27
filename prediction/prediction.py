import argparse
import json
import tempfile
import requests

from bs4 import BeautifulSoup
from configparser import ConfigParser
from io import BytesIO
from tika import parser

from translate_selenium import Translate

from ibm_botocore.client import Config, ClientError
from ibm_watson import PersonalityInsightsV3, DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

config = ConfigParser()
config.read("prediction.conf")

# parser = argparse.ArgumentParser(description='Provide required files for prediction.')
# parser.add_argument('--path-cxo-pdf-file', type=str,
#                     help="path to the pdf file that contains CXO's statement (e.g. annual report)")
# parser.add_argument('--path-news-list', type=str,
#                     help='path to txt file that contains list of news')
# parser.add_argument('--company-profitability', type=float,
#                     help="Profitability of a company from annual report.")

# args = parser.parse_args()

# PATH_TO_CXO_STATEMENT = args['path-cxo-pdf-file']
# PATH_TO_NEWS_LSIT = args['path-news-list']
# PROFITABILITY = args['company-profitability']

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


def get_self_expresion(filepath):
    
    content = parser.from_file(filepath)['content']
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

    if len(configs) != 0:
        config_id = configs[0]['configuration_id']
        return config_id
    else:
        with open('discovery_config.json', 'r') as config_data:
            data = json.load(config_data)
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

def get_overall_sentiment(filepath):
    
    with open(filepath, "r") as f:
        news_urls = f.read().split("\n")
    
    # Generator for content
    news_contents = (get_news_content(url) for url in news_urls)

    with tempfile.NamedTemporaryFile as tempfile:
        tempfile.name = tempfile.name + ".html"


    
    