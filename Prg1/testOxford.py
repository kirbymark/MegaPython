import api_config
import json
import requests
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse
from collections import defaultdict

def getDictdata(word_id,language):
    OxfordHeaders = {"app_id": api_config.oxfordDict_app_id, "app_key": api_config.oxfordDict_app_key}
    url = api_config.oxfordURL +'/entries/' + language + '/' + word_id.lower() + '/regions%3Dus%3Bdefinitions%3Bexamples'
    #print("Calling: " + url)

    response = requests.get(url, headers = OxfordHeaders)

    if response.status_code == 200:
        #print("Success")
        return response
    elif response.status_code == 404:
        return "The word does not exist"
    else:
        print("Error calling the OxfordAPI")
        print ("API Response Code: " + str(response.status_code))
        print ("API Response Text: " + str(response.text))
        return None

def ListEntries(source,expression):
    jsonpath_expr = parse(expression)
    #print("searching for: " + expression)
    result = []
    for match in jsonpath_expr.find(source):
        result.append(match.value)
    return result

print("Welcome to my word lookup program")
print("---------------------------------")
lookupword=input("Please enter a word to lookup: ")

response = getDictdata(lookupword,'en')
if isinstance(response, str):
    print(response)
else:
    responsePy = response.json()
    '''
    Trying  jsonpath
    '''
    wordtypes = ListEntries(responsePy,'results[*]..lexicalCategory')

    defs = defaultdict(list)

    for wtype in wordtypes:
        items = ListEntries(responsePy,'results[*]..lexicalEntries[?(@.lexicalCategory=="' + wtype + '")]..definitions[*]')
        defs[wtype] = items

        #print(defs)
        #print(type(defs))

        print("\n")
        print("The definition of " + lookupword + " is as follows:")
        print("-----------------------------------------")
        for i in defs.keys():
            print ("    " + str(i))
            for j in defs[i]:
                print ("       - " + str(j))


        quit()

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
