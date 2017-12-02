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

OutputData = {"Time":"","ETH_Price": "","ETH": "", "ETH_Val": "", "BTC_Price": "", "BTC": "", "BTC_Val": "", "USD_Val": "", "Total": ""}

with open(OutputFile, 'a+') as f:
    w = csv.writer(f,delimiter=',')
    if not file_exists:
        w.writerow(OutputData.keys())

OutputData["Time"] = str(now.format('YYYY-MM-DD-HHmmss'))

#Get Prices
myurl = api_url_base + '/products/ETH-USD/ticker'
response = requests.get(myurl)
ETH_PRICE = response.json()["price"]
print("Ether Price --> " + ETH_PRICE)

myurl = api_url_base + '/products/BTC-USD/ticker'
response = requests.get(myurl)
BTC_PRICE = response.json()["price"]
print("BitCoin Price --> " + BTC_PRICE)


OutputData["ETH_Price"] = float(ETH_PRICE)
OutputData["BTC_Price"] = float(BTC_PRICE)


# Account Details
myurl = api_url_base + '/accounts'
response = requests.get(myurl, auth=auth)

TotalAcctValue=0.0

for account in response.json():
    #print(account)
    if float(account["balance"]) > 0.0 and account["currency"]=="ETH":
        print(account["currency"]+" "+account["balance"]+"  Value:"+ str(float(account["balance"])*float(ETH_PRICE)))
        OutputData["ETH"] = float(account["balance"])
        OutputData["ETH_Val"] = float(account["balance"]) * float(ETH_PRICE)
        TotalAcctValue=TotalAcctValue+(float(account["balance"])*float(ETH_PRICE))
    elif float(account["balance"]) > 0.0 and account["currency"]=="BTC":
        print(account["currency"]+" "+account["balance"]+"  Value:"+ str(float(account["balance"])*float(BTC_PRICE)))
        OutputData["BTC"] = float(account["balance"])
        OutputData["BTC_Val"] = float(account["balance"])*float(BTC_PRICE)
        TotalAcctValue=TotalAcctValue+(float(account["balance"])*float(BTC_PRICE))
    elif float(account["balance"]) > 0.0:
        print(account["currency"]+" "+account["balance"]+"  Value:"+ str(float(account["balance"])))
        OutputData["USD_Val"] = float(account["balance"])
        TotalAcctValue=TotalAcctValue+(float(account["balance"]))

OutputData["Total"] = TotalAcctValue

print(TotalAcctValue)

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
