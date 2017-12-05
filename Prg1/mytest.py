import json
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

jsondata = json.load(open("jsondata.json"))
#print(jsondata)

def matchvals(expression):
    jsonpath_expr = parse(expression)
    print("----------------------------")
    print("searching for :" + str(jsonpath_expr))
    print("----------------------------")
    for match in jsonpath_expr.find(jsondata):
        print(match.value)
        print(match.full_path)


matchvals('$.store.book[*].author + " " + $.store.book[*].title')
matchvals('$..author')
matchvals('store.book.[2]')
matchvals('$.store.book[?(@.price < 10)]')
matchvals('$..book[?(@.price==8.95)]')
#
