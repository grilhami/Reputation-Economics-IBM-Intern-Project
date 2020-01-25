from ibm_watson import PersonalityInsightsV3, NaturalLanguageUnderstandingV1, DiscoveryV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from os.path import join, dirname
import json, csv, time

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

# Discovery Authenticator
authenticator = IAMAuthenticator('sT2M6WUORELnxZq6vXj7n53kwQbpf3Zj3G8vXlvQNsEE')
DiscoveryService = DiscoveryV1(
    version='2019-11-22',
    authenticator=authenticator
)
DiscoveryService.set_service_url('https://api.us-south.discovery.watson.cloud.ibm.com/instances/3e77ba4f-60f7-40cc-91ff-46d72fba9f29')

# Text Output
"""
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
"""

# CSV Output (no NLU)
def outputCSV(personality_insights, NLUService, company_name):
    with open('test-case.txt', encoding = 'utf-8') as profile_txt:
        response = personality_insights.profile(
            profile_txt.read(),
            accept="text/csv",
            content_type='text/plain;charset=utf-8',
            consumption_preferences=True,
            csv_headers=False,
            raw_scores=True).get_result()
    profile = response.content

    with open('resultsCSV.csv', 'a', newline='') as csvfile:
        penulis = csv.writer(csvfile, delimiter=',')
        cr = csv.reader(profile.decode('utf-8').splitlines())
        my_list = list(cr)
        for row in my_list:
            row.insert(0, company_name)
            penulis.writerow(row)
            print(row)

    print("Written to CSV file successfully!")

# Inference / Analysis with Discovery
def discoveryAnalysis(DiscoveryService):
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
    with open('config2.json', 'r') as config_data:
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

    # Add 3 new documents.
    with open('discovery-test-case-1.html', 'r', encoding='utf-8') as html:
        add_doc = DiscoveryService.add_document(environmentID, collectionID, file = html).get_result()
    print(json.dumps(add_doc, indent=2))

    with open('discovery-test-case-2.html', 'r', encoding='utf-8') as html:
        add_doc = DiscoveryService.add_document(environmentID, collectionID, file = html).get_result()
    print(json.dumps(add_doc, indent=2))

    with open('discovery-test-case-3.html', 'r', encoding='utf-8') as html:
        add_doc = DiscoveryService.add_document(environmentID, collectionID, file = html).get_result()
    print(json.dumps(add_doc, indent=2))

    # Wait for the documents to be processed.
    time.sleep(20)
    print("Documents maybe already processed? Let's go query.")

    # Query
    query_res = DiscoveryService.query(environmentID, collectionID).get_result()
    print(json.dumps(query_res, indent=2))
    hasil = json.dumps(query_res, indent=2)
    kamus = json.loads(hasil)

    # Get Sentiment
    numberofResults = kamus['matching_results']
    tempBarisStorage = []
    i = 0

    while i < numberofResults:
        tempBarisStorage.append(kamus['results'][i]['enriched_text']['sentiment']['document']['score'])
        print(tempBarisStorage[i])
        i += 1

    i = 0
    baris = 0
    # Count the average values of the sentiment.
    while i < numberofResults:
        baris = tempBarisStorage[i] + baris
        i += 1

    baris = baris / numberofResults

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
    # Obsolete: outputTxt(personality_insights, NLUService)  
    # Run this by changing the parameters.
    # outputCSV(personality_insights, NLUService, 'Gudang Garam Tbk.')
    discoveryAnalysis(DiscoveryService)

if __name__ == "__main__":
    main()