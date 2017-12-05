import api_config
import json
import requests
from jsonpath_ng import jsonpath, parse

def getDictdata(word_id,language):
    OxfordHeaders = {"app_id": api_config.oxfordDict_app_id, "app_key": api_config.oxfordDict_app_key}
    url = api_config.oxfordURL +'/entries/' + language + '/' + word_id.lower() + '/definitions%3Bexamples'
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


'''
Trying  jsonpath
'''
#jsonpath_expr = parse('entries[*].senses[*].definitions')
jsonpath_expr = parse('results[*]..senses[*].definitions[*]')

print("----------------------------")
print("searching for :" + str(jsonpath_expr))
print("----------------------------")
for match in jsonpath_expr.find(responsePy):
    print(match.full_path)
    print(match.value)

#location = parse(match.full_path)
#    for output in location.find(responsePy):
#        print(output)


'''
Trying  jsonpath
'''
#jsonpath_expr = parse('entries[*].senses[*].definitions')
jsonpath_expr = parse('results.[0].lexicalEntries.[0].entries.[0].senses.[0]..examples[*]')

print("----------------------------")
print("searching for :" + str(jsonpath_expr))
print("----------------------------")
for match in jsonpath_expr.find(responsePy):
    print(match.value)

    #print(match.__dict__)
#location = parse(match.full_path)
#    for output in location.find(responsePy):
#        print(output)
