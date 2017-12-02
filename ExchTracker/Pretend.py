from GDAXRequestAuth import *

profit_step=0.5
stop_ratio=0.1
Price30 = deque()
SMA_12_30 = deque()
SMA_26_30 = deque()


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
