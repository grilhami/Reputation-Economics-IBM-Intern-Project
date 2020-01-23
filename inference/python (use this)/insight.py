from ibm_watson import PersonalityInsightsV3, NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from os.path import join, dirname
import json
import csv

# Personality Insight Authenticator
authenticator = IAMAuthenticator('ECmiZK1SBaPna4NRiSjIwUkwZAJRAOf3vrkuhCfpZp88')
personality_insights = PersonalityInsightsV3(
    version='2017-10-13',
    authenticator=authenticator
)
personality_insights.set_service_url('https://api.us-south.personality-insights.watson.cloud.ibm.com/instances/1a6f55c5-2b27-4ad1-92a3-c36b6bf9de49')

# NLU Authenticator
authenticator = IAMAuthenticator('0TUqw2W7ZNzSn7sYo37SPm9JHK5VG7Fq9TWHoXuxItBy')
NLUService = NaturalLanguageUnderstandingV1(
    version='2019-07-12',
    authenticator=authenticator
)
NLUService.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/77166e19-c4c0-450f-a933-a9cfb4f058a6')

# Text Output
def outputTxt(personality_insights, NLUService):
    with open('test-case.txt', encoding = 'utf-8') as profile_txt:
        profile = personality_insights.profile(
            profile_txt.read(),
            accept="application/json",
            content_type='text/plain;charset=utf-8',
            consumption_preferences=True,
            content_language='en',
            raw_scores=True).get_result()
    print(json.dumps(profile, indent = 2))

    with open('personality-insight-results.txt', 'w') as jsonsaver:
        json.dump(profile, jsonsaver, indent = 2)

    print("Personality Insights's JSON written to text file successfully!")

    with open('test-case.txt', encoding='utf-8') as profile_txt:
        response = NLUService.analyze(
            text = profile_txt.read(),
            features = Features(
                entities=EntitiesOptions(emotion=True, sentiment=True, limit=5),
                keywords=KeywordsOptions(emotion=True, sentiment=True, limit=5)
            )
        ).get_result()
    print(json.dumps(response, indent = 2))

    with open('nlu-results.txt', 'w') as jsonsaver:
        json.dump(response, jsonsaver, indent = 2)

    print("NLU's JSON written to text file successfully!")

# CSV Output (currently no NLU)
def outputCSV(personality_insights, NLUService):
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

# Main Function
def main():
    outputTxt(personality_insights, NLUService)
    # outputCSV(personality_insights, NLUService)

if __name__ == "__main__":
    main()