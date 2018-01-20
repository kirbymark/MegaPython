import gdax
import pendulum
import os.path
import csv
import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
import api_config

# Create custom authentication for Exchange
class GDAXRequestAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())
        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request

environment="PROD"
Invested = 3800.0
ProdList = ["BTC","BCH","ETH","LTC","USD"]

if environment == "SANDBOX":
    api_url_base = 'https://api-public.sandbox.gdax.com'
    auth = GDAXRequestAuth(api_config.api_key_sand, api_config.api_secret_sand, api_config.passphrase_sand)
elif environment == "PROD":
    api_url_base = 'https://api.gdax.com'
    auth = GDAXRequestAuth(api_config.api_key_prod, api_config.api_secret_prod, api_config.passphrase_prod)

#OutputFlie info
now=pendulum.now()
pendulum.set_formatter('alternative')
OutputFile="GdaxAcctHistory.csv"
file_exists = os.path.isfile(OutputFile)

OutputData = {"Time":"", "Total": "","Gain": ""}
for item in ProdList:
    OutputData[item] = ""
    OutputData[item+"_Val"] = 0.0
    OutputData[item+"_Price"] = 0.0

print(OutputData)

with open(OutputFile, 'a+') as f:
    w = csv.writer(f,delimiter=',')
    if not file_exists:
        w.writerow(OutputData.keys())

OutputData["Time"] = str(now.format('YYYY-MM-DD-HHmmss'))

print("Time: " + str(now.format('YYYY-MM-DD-HHmmss')))
#Get Prices
for item in ProdList:
    if item == "USD":
            continue
    myurl = api_url_base + '/products/'+ item +'-USD/ticker'
    response = requests.get(myurl)
    OutputData[item+"_Price"] = float(response.json()["price"])
    #print(item + " Price is: " + str(OutputData[item+"_Price"]))

OutputData["USD_Price"]=1.0

# Account Details
myurl = api_url_base + '/accounts'
response = requests.get(myurl, auth=auth)

TotalAcctValue=0.0
#print(response.json())
#print("text \n" + response.text)

for account in response.json():
    for item in ProdList:
        if float(account["balance"]) > 0.0 and account["currency"]==item:
            OutputData[item] = float(account["balance"])
            OutputData[item+"_Val"] = float(account["balance"]) * OutputData[item+"_Price"]
            TotalAcctValue=TotalAcctValue + OutputData[item+"_Val"]
            print(account["currency"] + " Price: " + str(OutputData[item+"_Price"]) + "  Amount: " + str(OutputData[item]) + "  Value: " + str(OutputData[item+"_Val"]) )

OutputData["Total"] = TotalAcctValue
OutputData["Gain"] = float(TotalAcctValue) - Invested

print("Total: " + str(OutputData["Total"]) + "   Gain: " + str(OutputData["Gain"]) + "     Return:" + str(round(OutputData["Gain"]/OutputData["Total"]*100,2)))

#print(OutputData)

with open(OutputFile, 'a+') as f:
    w = csv.writer(f,delimiter=',')
    w.writerow(OutputData.values())


# An order
#order_url = api_url_base + '/orders'
#order_data = {
#    'type': 'market',
#    'side': 'buy',
#    'product_id': 'BTC-USD',
#    'size': '0.01'
#}
#response = requests.post(order_url, data=json.dumps(order_data), auth=auth)
#print(response.json())
