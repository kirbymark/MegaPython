import api_config
import json
import requests
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

def getDictdata(word_id,language):
    OxfordHeaders = {"app_id": api_config.oxfordDict_app_id, "app_key": api_config.oxfordDict_app_key}
    url = api_config.oxfordURL +'/entries/' + language + '/' + word_id.lower() + '/regions%3Dus%3Bdefinitions%3Bexamples'
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

lookupword="ace"

response = getDictdata(lookupword,'en')
responsePy = response.json()


'''
Trying  jsonpath
'''
#jsonpath_expr = parse('entries[*].senses[*].definitions')
jsonpath_expr = parse('results[*]..lexicalEntries[?(@.lexicalCategory=="Noun")]..definitions[*]')

print("----------------------------")
print( lookupword + " (Noun)")
print("----------------------------")
for match in jsonpath_expr.find(responsePy):
    #print(match.full_path)
    print("- " + match.value)

#jsonpath_expr = parse('entries[*].senses[*].definitions')
jsonpath_expr = parse('results[*]..lexicalEntries[?(@.lexicalCategory=="Verb")]..definitions[*]')

print("----------------------------")
print( lookupword + " (Verb)")
print("----------------------------")
for match in jsonpath_expr.find(responsePy):
    #print(match.full_path)
    print("- " + match.value)


#jsonpath_expr = parse('entries[*].senses[*].definitions')
#jsonpath_expr = parse('$..results[*]..lexicalEntries[?(@.lexicalCategory=="Verb")]..definitions[*] + " | Examples :" + $..results[*]..lexicalEntries[?(@.lexicalCategory=="Verb")]..senses..examples[*].text')
#jsonpath_expr = parse('$..results[*]..lexicalEntries[?(@.lexicalCategory=="Verb")]..senses..examples[*].text')
#jsonpath_expr = parse('$..results[*]..lexicalEntries[?(@.lexicalCategory=="Verb")]..definitions[*] + " aa " + $..results[*]..lexicalEntries[?(@.lexicalCategory=="Verb")]..senses..examples[*].text[*]')
#jsonpath_expr = parse('$..results[*]..lexicalEntries[?(@.lexicalCategory=="Verb")]..definitions[*] + " ex: " + $..results[*]..lexicalEntries[?(@.lexicalCategory=="Verb")]..definitions[*]..examples[*].text')
