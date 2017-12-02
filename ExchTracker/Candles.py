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


counter = 0
gran = 10
profit_step=0.5
stop_ratio=0.1
OutputData = {"Counter": "","Time": "", "Status": "", "HistDepth": "", "Price": "", "Close": "", "EMA_12": "", "EMA_26": "","Notes":"","Action":""}
PriceHist = deque(maxlen=300)
PriceHist.clear()
print(PriceHist)
EMA_12=0.0
EMA_26=0.0
STATUS="WARMING"

#OutputFlie info
now=pendulum.now()
pendulum.set_formatter('alternative')
OutputFile="CndleRun-" + now.format('YYYY-MM-DD-HHmmss') + ".csv"
file_exists = os.path.isfile(OutputFile)


with open(OutputFile, 'a+') as f:
    w = csv.writer(f,delimiter=',')
    if not file_exists:
        w.writerow(OutputData.keys())

#while True:
for x in range(0, 500):
    Currtime = pendulum.now()
    #print("Localtime: " + str(Currtime))
    #print("In UTC time: " + str(Currtime.in_timezone('Europe/London').isoformat()))
    #print(Currtime.isoformat())

    StartTime = Currtime.subtract(seconds=120)
    EndTime = Currtime

    #Get ETH Price
    myurl = api_url_base + '/products/ETH-USD/ticker'
    response = requests.get(myurl)
    ETH_PRICE = float(response.json()["price"])

    #Get Candle data
    myurl = api_url_base + '/products/ETH-USD/candles?start=' + StartTime.isoformat() + "&end=" + EndTime.isoformat() + "&granularity=" + str(gran)
    response = requests.get(myurl)
    ResponseData=response.json()

    #print("Request time from:" + str(StartTime.in_timezone('Europe/London').isoformat()) + " to " + str(EndTime.in_timezone('Europe/London').isoformat()))
    #print(ResponseData)
    addData(PriceHist,ResponseData)
    #for i in PriceHist:
    #    print(i)
    #    with open(OutputFile, 'a+') as f:
    #        w = csv.writer(f,delimiter=',')
    #        w.writerow(i.values())
    #print(PriceHist)


    #simple Moving Average
    #SMA_12= sum(deque(Price30,12))/len(deque(Price30,12))
    SMA_12 = SMA([item['Close'] for item in deque(PriceHist,maxlen=12)],len(deque(PriceHist,maxlen=12)))
    SMA_26 = SMA([item['Close'] for item in deque(PriceHist,maxlen=26)],len(deque(PriceHist,maxlen=26)))



    #exponetial moving Avg
    #print("PriceHist length " +str(len(PriceHist)))
    if len(PriceHist) > 24:
        values=[item['Close'] for item in deque(PriceHist)]
        window=12
        #print("-Calling EMA12- with: " +str(values) + " Window:" +str(window) )
        EMA_12=EMA(values,window)
        #print("-Returned-----" + str(EMA_12))
        #output = talib.EMA(np.asarray(values),timeperiod=12)
        #print(output)

    if len(PriceHist) > 50:
        values=[item['Close'] for item in deque(PriceHist)]
        window=26
        #print("-Calling EMA12- with: " +str(values) + " Window:" +str(window) )
        EMA_26=EMA(values,window)
        STATUS="READY"
        #print("-Returned-----" + str(EMA_26))
        #output = talib.EMA(np.asarray(values),timeperiod=12)
        #print(output)

    currentdata = PriceHist[-1]
    #print(currentdata["Close"])

    NOTES=""
    ACTION=""

    if STATUS == "READY":
        if ETH_PRICE > EMA_12:
            NOTES += "PRICE exceeds EMA12 by " + str(round(ETH_PRICE-EMA_12,2))
            if ETH_PRICE > EMA_26:
                NOTES += " and PRICE exceeds EMA26 by " + str(round(ETH_PRICE-EMA_26,2))
                ACTION += "Buy at " + str(round(ETH_PRICE+0.01,2)) + " to sell at "+ str(round(ETH_PRICE + 0.01 + profit_step,2))
            elif ETH_PRICE < EMA_26:
                NOTES += " but PRICE lower than EMA26 by " + str(round(EMA_26-ETH_PRICE,2))
            else:
                NOTES += ""
            if EMA_12 > EMA_26:
                NOTES += " and EMA12 exceeds EMA26 by " + str(round(EMA_12-EMA_26,2))
            elif EMA_12 < EMA_26:
                NOTES += " and EMA12 lower than EMA26 by " + str(round(EMA_26-EMA_12,2))
            else:
                NOTES += ""
        if ETH_PRICE < EMA_12:
            NOTES += "PRICE lower than EMA12 by " + str(round(EMA_12-ETH_PRICE,2))
            if ETH_PRICE < EMA_26:
                NOTES += " and PRICE lower than EMA26 by " + str(round(EMA_26-ETH_PRICE,2))
                ACTION += "Sell at " + str(round(ETH_PRICE-0.01,2)) + " to buy at "+ str(round(ETH_PRICE - 0.01 - profit_step,2))
            elif ETH_PRICE > EMA_26:
                NOTES += " but PRICE higher than EMA26 by " + str(round(ETH_PRICE-EMA_26,2))
            else:
                NOTES += ""
            if EMA_12 < EMA_26:
                NOTES += " and EMA12 lower than EMA26 by " + str(round(EMA_26-EMA_12,2))
            elif EMA_12 > EMA_26:
                NOTES += " and EMA12 exceeds EMA26 by " + str(round(EMA_12-EMA_26,2))
            else:
                NOTES += ""

    OutputData["Counter"] = str(x)
    OutputData["Time"] = Currtime
    OutputData["Status"] = STATUS
    OutputData["HistDepth"] = len(PriceHist)
    OutputData["Price"] = round(ETH_PRICE,2)
    OutputData["Close"] = currentdata["Close"]
    OutputData["EMA_12"] = round(EMA_12,2)
    OutputData["EMA_26"] = round(EMA_26,2)
    OutputData["Notes"] = NOTES
    OutputData["Action"] = ACTION

    #print(OutputData)

    with open(OutputFile, 'a+') as f:
        w = csv.writer(f,delimiter=',')
        w.writerow(OutputData.values())

    time.sleep(2)



#myurl = api_url_base + '/products/ETH-USD/book?level=1'
#print(myurl)
#response = requests.get(myurl)
#myList=response.json()
#print(myList.keys())
#print(myList.values())
#for i in myList:
#    print(type(i))



#print(*myList, sep='\n')

#print(response.json())
