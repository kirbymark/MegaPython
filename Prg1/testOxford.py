import api_config
import json
import requests

OxfordHeaders = {"app_id": api_config.oxfordDict_app_id, "app_key": api_config.oxfordDict_app_key}
#OxfordHeaders = {"app_id": "123", "app_key": api_config.oxfordDict_app_key}
print(OxfordHeaders)

word_id = 'hello'
language='en'

url = api_config.oxfordURL +'/entries/' + language + '/' + word_id.lower() + '/regions=us'
print(url)

response = requests.get(url, headers = OxfordHeaders)


if response.status_code == 200:
    print("code {}\n".format(response.status_code))
    print("text \n" + response.text)
    print("json \n" + json.dumps(response.json()))
else:
    print("Error calling the OxfordAPI")
    print ("API Response Code: " + str(response.status_code))
    print ("API Response Text: " + str(response.text))
