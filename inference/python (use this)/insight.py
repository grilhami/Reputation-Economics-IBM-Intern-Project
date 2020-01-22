from ibm_watson import PersonalityInsightsV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from os.path import join, dirname
import json
import csv

authenticator = IAMAuthenticator('ECmiZK1SBaPna4NRiSjIwUkwZAJRAOf3vrkuhCfpZp88')
personality_insights = PersonalityInsightsV3(
    version='2017-10-13',
    authenticator=authenticator
)
personality_insights.set_service_url('https://api.us-south.personality-insights.watson.cloud.ibm.com/instances/1a6f55c5-2b27-4ad1-92a3-c36b6bf9de49')

# Text Output
"""
with open('test-case.txt', encoding = 'utf-8') as profile_txt:
    profile = personality_insights.profile(
        profile_txt.read(),
        accept="application/json",
        content_type='text/plain;charset=utf-8',
        consumption_preferences=True,
        content_language='en',
        raw_scores=True).get_result()
print(json.dumps(profile, indent = 2))

with open('results.txt', 'w') as jsonsaver:
    json.dump(profile, jsonsaver, indent = 2)

print("Written to text file successfully!")
"""

# CSV Output (commented right now)
with open('test-case.txt', encoding = 'utf-8') as profile_txt:
    response = personality_insights.profile(
        profile_txt.read(),
        accept="text/csv",
        content_type='text/plain;charset=utf-8',
        consumption_preferences=True,
        csv_headers=True,
        raw_scores=True).get_result()

profile = response.content

with open('resultsCSV.csv', 'w', newline='') as csvfile:
    penulis = csv.writer(csvfile, delimiter=',')
    cr = csv.reader(profile.decode('utf-8').splitlines())
    my_list = list(cr)
    for row in my_list:
        penulis.writerow(row)
        print(row)

print("Written to CSV file successfully!")
