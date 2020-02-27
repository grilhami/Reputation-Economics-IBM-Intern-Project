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