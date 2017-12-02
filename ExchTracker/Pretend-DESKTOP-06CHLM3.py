import gdax
import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
import api_config
import csv
import os.path
import pendulum
import dateutil.parser
from collections import deque

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

OutputFile='output3.csv'
file_exists = os.path.isfile(OutputFile)

environment="PROD"

if environment == "SANDBOX":
    api_url_base = 'https://api-public.sandbox.gdax.com'
    auth = GDAXRequestAuth(api_config.api_key_sand, api_config.api_secret_sand, api_config.passphrase_sand)
elif environment == "PROD":
    api_url_base = 'https://api.gdax.com'
    auth = GDAXRequestAuth(api_config.api_key_prod, api_config.api_secret_prod, api_config.passphrase_prod)

profit_step=0.2
Price30 = deque()
SMA_12_30 = deque()
SMA_26_30 = deque()


def buy(Acct,price):
    Acct["USD"] = Acct["USD"] - price
    Acct["ETH"] = Acct["ETH"] + 1.0

def sell(Acct,price):
    Acct["USD"] = Acct["USD"] + price
    Acct["ETH"] = Acct["ETH"] - 1.0

def add_amt_deque30(mylist,price):
    mylist.append(price)
    new_list=deque(mylist,30)
    #print("New: " + str(list(new_list)))
    return new_list


Acct1= {'USD': 1000.0, 'ETH': 2.0 }
Acct2= {'USD': 1000.0, 'ETH': 2.0 }

tz = pendulum.timezone('America/New_York')
public_client = gdax.PublicClient()

counter = 0
MarketData = { "Counter": "", "Time": "", "Price": "", "SMA_12": "", "SMA_26": "", "Price_slope":"","SMA_12_slope":"", "SMA_26_slope":"", "Acct1": "", "Acct2": "" }

with open(OutputFile, 'a+') as f:
    w = csv.writer(f,delimiter=',')
    if not file_exists:
        w.writerow(MarketData.keys())

oldtimestamp=""



while True:
    #Get ETH Price
    myurl = api_url_base + '/products/ETH-USD/ticker'
    response = requests.get(myurl)
    ETH_PRICE = response.json()["price"]
    #print("oldtime: " + str(oldtimestamp) + "     newtime: " + tz.convert(dateutil.parser.parse(response.json()["time"])).strftime("%Y-%m-%d %H:%M:%S"))
    while response.json()["time"] == oldtimestamp:
        time.sleep(0.33)
        response = requests.get(myurl)
        #print("Inner loop   oldtime: " + str(oldtimestamp) + "     newtime: " + tz.convert(dateutil.parser.parse(response.json()["time"])).strftime("%Y-%m-%d %H:%M:%S"))
    oldtimestamp = response.json()["time"]


    #print("Ether Price --> " + ETH_PRICE)

    #data = public_client.get_product_ticker(product_id='ETH-USD')
    #data['nyc_time']= str(tz.convert(dateutil.parser.parse(data["time"])))
    #data['nyc_time']= tz.convert(dateutil.parser.parse(data["time"])).strftime("%Y-%m-%d %H:%M:%S")
    #print(str(i)+" | "+data["price"]+" | "+data["nyc_time"]+" | "+str(Acct1["USD"])+" - "+str(Acct1["ETH"])+" | "+str(Acct2["USD"])+" - "+str(Acct2["ETH"]))

    Price30=add_amt_deque30(Price30,float(response.json()["price"]))
    Price_slope=((deque(Price30,3)[-1] - deque(Price30,3)[0]) / 2)

    SMA_12= sum(deque(Price30,12))/len(deque(Price30,12))
    SMA_12_30=add_amt_deque30(SMA_12_30,SMA_12)
    SMA_12_slope=((deque(SMA_12_30,3)[-1] - deque(SMA_12_30,3)[0]) / 2)

    SMA_26= sum(deque(Price30,26))/len(deque(Price30,26))
    SMA_26_30=add_amt_deque30(SMA_26_30,SMA_26)
    SMA_26_slope=((deque(SMA_26_30,3)[-1] - deque(SMA_26_30,3)[0]) / 2)

    MarketData["Counter"] = str(counter)
    MarketData["Time"] = tz.convert(dateutil.parser.parse(response.json()["time"])).strftime("%Y-%m-%d %H:%M:%S")
    MarketData["Price"] = response.json()["price"]
    MarketData["SMA_12"] = str(SMA_12)
    MarketData["SMA_26"] = str(SMA_26)
    MarketData["Price_slope"] = str(Price_slope)
    MarketData["SMA_12_slope"] = str(SMA_12_slope)
    MarketData["SMA_26_slope"] = str(SMA_26_slope)
    MarketData["Acct1"] = str(Acct1["USD"]) + " - " + str(Acct1["ETH"])
    MarketData["Acct2"] = str(Acct2["USD"]) + " - " + str(Acct2["ETH"])

    #print(MarketData.keys())
    print(MarketData.values())
    #print(str(i)+" | "+tz.convert(dateutil.parser.parse(response.json()["time"])).strftime("%Y-%m-%d %H:%M:%S")+" | "+response.json()["price"]+" | "+str(SMA_12)+" | "+str(SMA_26)+" | "+ str(Acct1["USD"]) +" - " + str(Acct1["ETH"])+" | "+str(Acct2["USD"])+" - "+str(Acct2["ETH"]))

    with open(OutputFile, 'a+') as f:
        w = csv.writer(f,delimiter=',')
        w.writerow(MarketData.values())
    counter += 1
    time.sleep(2)







#get the data from GDAX API
