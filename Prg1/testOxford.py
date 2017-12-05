import api_config
import json
import requests
from jsonpath_ng import jsonpath, parse
import pandas as pd


def getDictdata(word_id,language):
    OxfordHeaders = {"app_id": api_config.oxfordDict_app_id, "app_key": api_config.oxfordDict_app_key}
    url = api_config.oxfordURL +'/entries/' + language + '/' + word_id.lower() + '/regions=us'
    print("Calling: " + url)

    response = requests.get(url, headers = OxfordHeaders)

    if response.status_code == 200:
        print("Success")
        return response
    else:
        print("Error calling the OxfordAPI")
        print ("API Response Code: " + str(response.status_code))
        print ("API Response Text: " + str(response.text))
        return None


response = getDictdata('rain','en')
responsePy = response.json()
output=responsePy["results"][0]["lexicalEntries"]
#print(type(output))
#print(len(output))
#print(output[0])
#print(output[1])
print(output[1]["entries"][0]["senses"][0]["definitions"])
print(output[0]["entries"][0]["senses"][0]["definitions"])

'''
Trying  pandas
'''

df = pd.io.json.json_normalize(responsePy)
df.columns = df.columns.map(lambda x: x.split(".")[-1])
print (df)


'''
Trying  jsonpath
#jsonpath_expr = parse('entries[*].senses[*].definitions')
jsonpath_expr = parse('provider[*]')
print(jsonpath_expr)

for match in jsonpath_expr.find(responsePy):
    print(match)

'''
