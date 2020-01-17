from ibm_watson import PersonalityInsightsV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from os.path import join, dirname
import json

authenticator = IAMAuthenticator('ECmiZK1SBaPna4NRiSjIwUkwZAJRAOf3vrkuhCfpZp88')
personality_insights = PersonalityInsightsV3(
    version='2017-10-13',
    authenticator=authenticator
)
personality_insights.set_service_url('https://api.us-south.personality-insights.watson.cloud.ibm.com/instances/1a6f55c5-2b27-4ad1-92a3-c36b6bf9de49')

with open('test-case.txt', encoding = 'utf-8') as profile_txt:
    profile = personality_insights.profile(
        profile_txt.read(),
        accept="application/json",
        content_type='text/plain;charset=utf-8',
        consumption_preferences=True,
        raw_scores=True)
print(profile)