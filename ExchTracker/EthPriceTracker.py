from GDAXRequestAuth import *
import time
import datetime
import collections
import numpy as np
import pandas as pd
import talib

tz = pendulum.timezone('America/New_York')
public_client = gdax.PublicClient()

def addData(currdata,newdata):
    mydict=dict()
    for i in reversed(newdata):
        #print("searching for: "+str(pendulum.from_timestamp(i[0])))
        if not any(d["Time"] == str(pendulum.from_timestamp(i[0])) for d in currdata):
            mydict["Time"] = str(pendulum.from_timestamp(i[0]))
            mydict["Low"] = i[1]
            mydict["High"] = i[2]
            mydict["Open"] = i[3]
            mydict["Close"] = i[4]
            mydict["Volume"] = i[5]
            currdata.append(mydict.copy())


        #mylist.append(price)
        #new_list=deque(mylist,30)
        #print("New: " + str(list(new_list)))
    return currdata

def SMA(values, window):
    weights = np.repeat(1.0,window)/window
    smas = np.convolve(values,weights,'valid')
    return smas

def EMA(values, window):
    #print("Infunction")
    df = pd.DataFrame(values,columns=["values"])
    ema = df.ewm(span=window,min_periods=window,adjust=False).mean()
    #print(ema)
    EMA=ema.values[-1].tolist()[0]
    return EMA

#Alternate version of EMA
#def TEMA(values, window):
    #print("Infunction")
    #ema_result=talib.EMA(np.asarray(values), timeperiod=window)
    #print(ema_result)
    #return float(ema_result[-1])

counter = 0
gran = 300
profit_step=0.5
stop_ratio=0.1
StoreData = {"Type":"","Time": "", "HistDepth": "", "Price": "", "EMA_12": "", "EMA_26": ""}
OutData = {"Time": "", "HistDepth": "", "Price": "", "EMA_12": "", "EMA_26": ""}
PriceHist = deque(maxlen=500)
PriceHist.clear()
EMA_12=0.0
EMA_26=0.0


#StoreFlie info
now=pendulum.now()
pendulum.set_formatter('alternative')
StoreFile="EthPriceTrack.txt"

#OutputFlie info
now=pendulum.now()
pendulum.set_formatter('alternative')
OutFile="TrackerRun-" + now.format('YYYY-MM-DD-HHmmss') + ".csv"



print("Running ... yes ....")

while True:
    Currtime = pendulum.now()
    #print("Localtime: " + str(Currtime))
    #print("In UTC time: " + str(Currtime.in_timezone('Europe/London').isoformat()))
    #print(Currtime.isoformat())

    StartTime = Currtime.subtract(seconds=gran*4)
    EndTime = Currtime

    #Get ETH Price
    myurl = api_url_base + '/products/ETH-USD/ticker'
    response = requests.get(myurl)
    ETH_PRICE = float(response.json()["price"])

    #Get Candle data
    myurl = api_url_base + '/products/ETH-USD/candles?start=' + StartTime.isoformat() + "&end=" + EndTime.isoformat() + "&granularity=" + str(gran)
    response = requests.get(myurl)
    try:
        ResponseData=response.json()
    except json.decoder.JSONDecodeError:
        print("Decoding JSON has failed")


    addData(PriceHist,ResponseData)

    #simple Moving Average
    SMA_12 = SMA([item['Close'] for item in deque(PriceHist,maxlen=12)],len(deque(PriceHist,maxlen=12)))
    SMA_26 = SMA([item['Close'] for item in deque(PriceHist,maxlen=26)],len(deque(PriceHist,maxlen=26)))

    #exponetial moving Avg
    if len(PriceHist) > 24:
        values=[item['Close'] for item in deque(PriceHist)]
        window=12
        EMA_12=EMA(values,window)



    #if len(PriceHist) > 50:
    if len(PriceHist) > 35:
        values=[item['Close'] for item in deque(PriceHist)]
        window=26
        EMA_26=EMA(values,window)


    currentdata = PriceHist[-1]

    StoreData["Type"] = "Pandas"
    StoreData["Time"] = Currtime
    StoreData["HistDepth"] = len(PriceHist)
    StoreData["Price"] = round(ETH_PRICE,3)
    #OutputData["Close"] = currentdata["Close"]
    StoreData["EMA_12"] = round(EMA_12,3)
    StoreData["EMA_26"] = round(EMA_26,3)


    #print(OutputData)

    with open(StoreFile, 'w') as f:
        w = csv.writer(f,delimiter=',')
        w.writerow(StoreData.values())


    OutData["Time"] = Currtime
    OutData["HistDepth"] = len(PriceHist)
    OutData["Price"] = round(ETH_PRICE,3)
    OutData["EMA_12"] = round(EMA_12,3)
    OutData["EMA_26"] = round(EMA_26,3)


        #print(OutputData)

    with open(OutFile, 'a+') as f:
        w = csv.writer(f,delimiter=',')
        w.writerow(OutData.values())


    time.sleep(200)
