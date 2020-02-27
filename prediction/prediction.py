import argparse
import requests

from bs4 import BeautifulSoup
from configparser import Configparser
from io import BytesIO

from translate_selenium import Translate

from ibm_botocore.client import Config, ClientError
from ibm_watson import PersonalityInsightsV3, DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

config = Configparser()
config.read("prediction.conf")

parser = argparse.ArgumentParser(description='Provide required files for prediction.')
parser.add_argument('--path-cxo-pdf-file', type=str,
                    help="path to the pdf file that contains CXO's statement (e.g. annual report)")
parser.add_argument('--path-news-list', type=str,
                    help='path to txt file that contains list of news')
parser.add_argument('--company-profitability', type=float,
                    help="Profitability of a company from annual report.")

args = parser.parse_args()

PATH_TO_CXO_STATEMENT = args['path-cxo-pdf-file']
PATH_TO_NEWS_LSIT = args['path-news-list']
PROFITABILITY = args['company-profitability']

PERSONALITY_INSIGHT_AUTHENTICATOR = config['personality-insight']['apikey']
PERSONALITY_INSIGHT_SERVICE_URL = config['personality-insight']['url']
DISCOVERY_AUTHENTICATOR = config['discovery']['apikey']
DISCOVERY_SERVICE_URL = config['discovery']['url']


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


def get_self_expresion(filepath):
    
    data = open(filepath, "r")




