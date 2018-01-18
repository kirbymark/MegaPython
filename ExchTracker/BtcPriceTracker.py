from GDAXRequestAuth import *
import time
# import datetime
# import collections
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from requests.adapters import HTTPAdapter
from matplotlib import style
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, DateFormatter, drange
# import talib

tz = pendulum.timezone('America/New_York')
public_client = gdax.PublicClient()


# The addData function appends new price data to an array of price history
def addData(currdata, newdata):
    mydict = dict()
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

def TheMax(values):
    return max(values)

def TheMin(values):
    return min(values)

def TheMid(values):
    return (max(values) + min(values)) / 2.0


def GetTradeData(timewindow):
    Currtime = pendulum.now()

    StartTime = Currtime.subtract(seconds=timewindow)
    EndTime = Currtime
    #print("Getting history from " + str(StartTime) + " to " + str(Currtime))

    #Get Candle data
    myurl = api_url_base + '/products/BTC-USD/candles?start=' + StartTime.isoformat() + "&end=" + EndTime.isoformat() + "&granularity=" + str(granularity)
    #print(myurl)
    response = requests.get(myurl)
    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        print("Decoding JSON has failed")
        return none

def getBTCprice():
    myurl = api_url_base + '/products/BTC-USD/ticker'
    response = requests.get(myurl)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        print("Error: " + str(e))
        return 0.0

    return float(response.json()["price"])



def plotData(Dataset):
    Close_price=[item['Close'] for item in deque(Dataset)]
    Open_price=[item['Open'] for item in deque(Dataset)]
    #Convert the ISO string to datetime and adjust for current timezone
    Time_stmp=[(datetime.strptime(item['Time'], '%Y-%m-%dT%H:%M:%S+00:00')- timedelta(hours=5)) for item in deque(Dataset)]
    dataSeries1 = pd.Series(Close_price, index=Time_stmp)
    dataSeries2 = pd.Series(Open_price, index=Time_stmp)
    dataSeries1.plot(ax=myplot, style='v-', label='close')
    dataSeries2.plot(ax=myplot, style='o', label='open')
    myplot.grid(color='#a6a6a6', linestyle='--', linewidth=1)
    myplot.legend(loc='upper left')
    figure.canvas.draw()

    #ax.xaxis.set_minor_locator(HourLocator)
    myplot.xaxis.grid(True, which="minor")

    #plt.show()

s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries=3))

counter = 0
granularity = 15  # min intervals
PriceHist = deque(maxlen=500)
PriceHist.clear()
EMA_12=0.0
EMA_26=0.0
E_Max=0.0
E_Min=0.0
E_Mid=0.0

#StoreFile name and format info
StoreFile=".\output\BtcPriceTrack.txt"
StoreData = {"Type":"","Time": "", "HistDepth": "", "Price": "", "EMA_12": "", "EMA_26": "", "Max": "", "Min": "", "Mid": ""}

#OutputFlie name and format info
now=pendulum.now()
pendulum.set_formatter('alternative')
OutFile=".\output\TrackerRunBTC-" + now.format('YYYY-MM-DD-HHmmss') + ".csv"
OutData = {"Time": "", "HistDepth": "", "Price": "", "EMA_12": "", "EMA_26": "", "Max": "", "Min": "", "Mid": ""}

#plt.ion()
#figure = plt.figure(figsize=(10,7), dpi=100)
#figure=plt.gcf()
#figure=plt.figure(figsize=(12,10), dpi=100)
#figure.show()
#figure.canvas.draw()
#myplot = figure.add_subplot(111)
#myplot.set(title='Price History', xlabel='Time', ylabel='Price')
#style.use("ggplot")


print("stating...")
addData(PriceHist,GetTradeData(granularity*300))
#plotData(PriceHist)
#plt.draw()
#plt.pause(1)
#plt.show(block=True)
#quit()

#ani = animation.FuncAnimation(fig,animate,interval=1000)
#plt.show()

#viz.xaxis.set_major_locator(DayLocator())
#viz.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
#viz.xaxis.set_minor_locator(MinuteLocator())
#ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
#ax.xaxis.set_minor_locator(MinuteLocator())

#viz.set_xticks(dataSeries.index)
#viz.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))


while True:
    addData(PriceHist,GetTradeData(granularity*4))
    #print("Depth of PriceHist: " + str(len(PriceHist)))
    #plotData(PriceHist)

    BTC_PRICE = getBTCprice()

    #simple Moving Average
    SMA_12 = SMA([item['Close'] for item in deque(PriceHist,maxlen=12)],len(deque(PriceHist,maxlen=12)))
    SMA_26 = SMA([item['Close'] for item in deque(PriceHist,maxlen=26)],len(deque(PriceHist,maxlen=26)))
    E_Max = TheMax([item['Close'] for item in deque(PriceHist,maxlen=360)])
    E_Min = TheMin([item['Close'] for item in deque(PriceHist,maxlen=360)])
    E_Mid = TheMid([item['Close'] for item in deque(PriceHist,maxlen=360)])


    #exponetial moving Avg
    if len(PriceHist) > 24:
        values=[item['Close'] for item in deque(PriceHist)]
        window=12
        EMA_12=EMA(values,window)



    #if len(PriceHist) > 50:
    if len(PriceHist) > 48:
        values=[item['Close'] for item in deque(PriceHist)]
        window=26
        EMA_26=EMA(values,window)


    currentdata = PriceHist[-1]

    StoreData["Type"] = "Pandas"
    StoreData["Time"] = pendulum.now()
    StoreData["HistDepth"] = len(PriceHist)
    StoreData["Price"] = round(BTC_PRICE,3)
    #OutputData["Close"] = currentdata["Close"]
    StoreData["EMA_12"] = round(EMA_12,3)
    StoreData["EMA_26"] = round(EMA_26,3)
    StoreData["Max"] = round(E_Max,3)
    StoreData["Min"] = round(E_Min,3)
    StoreData["Mid"] = round(E_Mid,3)



    #print(OutputData)

    with open(StoreFile, 'w') as f:
        w = csv.writer(f,delimiter=',')
        w.writerow(StoreData.values())


    OutData["Time"] = pendulum.now()
    OutData["HistDepth"] = len(PriceHist)
    OutData["Price"] = round(BTC_PRICE,3)
    OutData["EMA_12"] = round(EMA_12,3)
    OutData["EMA_26"] = round(EMA_26,3)
    OutData["Max"] = round(E_Max,3)
    OutData["Min"] = round(E_Min,3)
    OutData["Mid"] = round(E_Mid,3)



        #print(OutputData)

    with open(OutFile, 'a+') as f:
        w = csv.writer(f,delimiter=',')
        w.writerow(OutData.values())

    print("waiting...")
    time.sleep(20)
    #plt.clf()
