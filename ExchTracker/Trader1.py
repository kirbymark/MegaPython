from GDAXRequestAuth import *
import time
import datetime
import collections
import numpy as np
import pandas as pd
import talib

def FlowState(PRICE,EMA12,EMA26):
    state="UNDEF"
    delta = 0.02
    if PRICE > (EMA12 + delta) and EMA12 > (EMA26 + delta):
        state="UP"
    if EMA12 > (PRICE + delta) and PRICE > (EMA26 + delta):
        state="DIP"
    if EMA12 > (EMA26 + delta) and EMA26 > (PRICE + delta):
        state="DDIP"
    if EMA26 > (EMA12 + delta) and EMA12 > (PRICE + delta):
        state="DOWN"
    if EMA26 > (PRICE + delta) and PRICE > (EMA12 + delta):
        state="RISE"
    if PRICE > (EMA26 + delta) and EMA26 > (EMA12 + delta):
        state="DRISE"
    return state

def addData(currdata,newdata):
    currdata.append(newdata)
    new_list=deque(currdata,5)
    return new_list

def PlaceOrder(type,side,price):
    myurl = api_url_base + '/orders'
    order_data = {
        'type': type,
        'side': side,
        'product_id': 'ETH-USD',
        'size': '0.01',
        'price': price
    }
    response = requests.post(myurl, data=json.dumps(order_data), auth=auth)
    if response.status_code is not 200:
        raise Exception('Invalid GDAX Status Code: %d' % response.status_code)

    return response.json()["id"]

def CancelOrder(order_id):
    myurl = api_url_base + '/orders/' + order_id
    response = requests.delete(myurl, auth=auth)


def GetOrders():
    myurl = api_url_base + '/orders'
    response = requests.get(myurl, auth=auth)
    result = response.json()
    return result

def GetFills():
    myurl = api_url_base + '/fills'
    response = requests.get(myurl, auth=auth)
    result = response.json()
    return result

tz = pendulum.timezone('America/New_York')
public_client = gdax.PublicClient()

TrackerFile = "EthPriceTrack.txt"
environment="PROD"

if environment == "SANDBOX":
    api_url_base = 'https://api-public.sandbox.gdax.com'
    auth = GDAXRequestAuth(api_config.api_key_sand, api_config.api_secret_sand, api_config.passphrase_sand)
elif environment == "PROD":
    api_url_base = 'https://api.gdax.com'
    auth = GDAXRequestAuth(api_config.api_key_prod, api_config.api_secret_prod, api_config.passphrase_prod)


counter = 0
gran = 10
profit_step=1.6
stop_ratio=0.1

OutputData = {"Counter": "","Time": "", "Status": "", "HistDepth": "", "Price": "", "Close": "", "EMA_12": "", "EMA_26": "","Notes":"","Action":""}

#OutputFlie info
now=pendulum.now()
pendulum.set_formatter('alternative')
OutputFile="TraderRun-" + now.format('YYYY-MM-DD-HHmmss') + ".csv"
file_exists = os.path.isfile(OutputFile)

STATE = deque(maxlen=5)
STATE.clear()
ACTION="NONE"

#PlaceOrder('limit','buy','300.00')
#orders = GetOrders()

#for i in orders:
    #print(orders)
    #print(" ID:"+ i["id"] + " seeks to " + i["side"] + " " + i["size"] + " at " + i["price"])

#while True:
for x in range(0, 500):

    #Get PriceData
    PriceReader = csv.reader(open(TrackerFile,newline="\n"),delimiter=',')
    for i in PriceReader:
        PRICE = float(i[3])
        EMA12 = float(i[4])
        EMA26 = float(i[5])

    if EMA26 > 0.0:
        currentSTATE=FlowState(PRICE,EMA12,EMA26)
        addData(STATE,currentSTATE)

        print(currentSTATE + "   Price(" + str(PRICE)+")  EMA12("+str(EMA12)+")  EMA26("+str(EMA26)+")       " + str(STATE) + "    Action: " + ACTION)
        if len(STATE) > 3:
            if ACTION == "NONE" and STATE[-1] == "UP" and ( STATE[-2] == "UNDEF" or STATE[-2] == "UP" ):
                #STEPUP
                BuyPrice = PRICE
                #BuyPrice = PRICE - 0.01
                BuyOrder = PlaceOrder('limit','buy',str(round(BuyPrice,2)))
                print("Buy at " + str(BuyPrice) + " OrderID:" + BuyOrder)
                #BuyOrder = "cca41d4b-8530-42c9-853d-98be9356c4d3"
                ACTION = "BUYSTEP1"

            orders = GetOrders()
            fills = GetFills()

            #print(fills)

            if ACTION == "BUYSTEP1":
                #Check if BUY ORDER completed
                if any(f['order_id'] == BuyOrder for f in fills):
                    #if BuyOrder in fills.values():
                    SellPrice = BuyPrice + profit_step
                    print("Buy complete - placing sell")
                    #place the sell
                    SellOrder = PlaceOrder('limit','sell',str(SellPrice))
                    #SellOrder = "cca41d4b-8530-42c9-853d-98be9356c4d3"
                    #SellOrder = "newcca41d4b-8530-42c9-853d-98be9356c4d3"
                    print("Sell at " + str(SellPrice) + " OrderID:" + SellOrder)
                    ACTION = "BUYSTEP2"
                else:
                    print("Buy still pending")

            if ACTION == "BUYSTEP2":
                #Check if we want to raise the SELL ORDER
                #first Check if Sell still open
                fills = GetFills()

                if any(f['order_id'] == SellOrder for f in fills):
                    print("Sell Complete sold at " + str(SellPrice))
                    ACTION="NONE"
                else:
                    print("Sell still pending ... looking for " + str(SellPrice) + " only " + str(round(PRICE - SellPrice,2)) + " more" )
                    if (STATE[-1] == "UP" and STATE[-2] == "UP" and STATE[-3] == "UP" and STATE[-4] == "UP" and STATE[-5] == "UP") and ((SellPrice - PRICE) < 0.02):
                        NewSellPrice = round(SellPrice + 0.02,2)
                        print("Raise sell from " + str(SellPrice) + " to " + str(NewSellPrice))
                        NewSellOrder = PlaceOrder('limit','sell',str(NewSellPrice))
                        CancelOrder(SellOrder)
                        SellPrice=NewSellPrice
                        SellOrder=NewSellOrder

            if ACTION == "NONE" and STATE[-1] == "DOWN" and ( STATE[-2] == "UNDEF" or STATE[-2] == "DOWN" ):
                #STEPDOWN
                #SellPrice = PRICE + 0.01
                SellPrice = PRICE
                SellOrder = PlaceOrder('limit','sell',str(SellPrice))
                #SellOrder = "cca41d4b-8530-42c9-853d-98be9356c4d3"
                print("Sell at " + str(SellPrice) + " OrderID:" + SellOrder)

                ACTION = "SELLSTEP1"

            orders = GetOrders()
            fills = GetFills()

            if ACTION == "SELLSTEP1":
                #Check if Sell ORDER completed
                if any(f['order_id'] == SellOrder for f in fills):
                    BuyPrice = SellPrice - profit_step
                    print("Sell complete - place buy")
                    #place the sell
                    BuyOrder = PlaceOrder('limit','buy',str(BuyPrice))
                    #BuyOrder = "cca41d4b-8530-42c9-853d-98be9356c4d3"
                    #BuyOrder = "newcca41d4b-8530-42c9-853d-98be9356c4d3"
                    print("Buy at " + str(BuyPrice) + " OrderID:" + BuyOrder)
                    ACTION = "SELLSTEP2"
                else:
                    print("Sell still pending")

            if ACTION == "SELLSTEP2":
                #Check if we want to lower the SELL ORDER
                #first Check if Buy still open
                fills = GetFills()

                if any(f['order_id'] == BuyOrder for f in fills):
                    #already bought
                    print("BUY Complete - bought at " + str(BuyPrice))
                    ACTION="NONE"
                else:
                    print("BUY still pending .... looking for "+ str(BuyPrice) + " only " + str(PRICE-BuyPrice) + " remaining" )
                    if (STATE[-1] == "DOWN" and STATE[-2] == "DOWN" and STATE[-3] == "DOWN" and STATE[-4] == "DOWN" and STATE[-5] == "DOWN") and ((PRICE-BuyPrice) < 0.02):
                        NewBuyPrice = round(BuyPrice - 0.02,2)
                        print("Lowered buy from " + str(BuyPrice) + " to " + str(NewBuyPrice))
                        NewBuyOrder = PlaceOrder('limit','buy','str(NewBuyPrice)')
                        CancelOrder(BuyOrder)
                        BuyPrice=NewBuyPrice
                        BuyOrder=NewBuyOrder

        #print(len(orders))

    #OutputData["Counter"] = str(x)
    #OutputData["Time"] = Currtime
    #OutputData["Status"] = STATUS
    #OutputData["HistDepth"] = len(PriceHist)
    #OutputData["Price"] = round(ETH_PRICE,2)
    #OutputData["Close"] = currentdata["Close"]
    #OutputData["EMA_12"] = round(EMA_12,2)
    #OutputData["EMA_26"] = round(EMA_26,2)
    #OutputData["Notes"] = NOTES
    #OutputData["Action"] = ACTION

    #print(OutputData)

    #with open(OutputFile, 'a+') as f:
    #    w = csv.writer(f,delimiter=',')
    #    w.writerow(OutputData.values())

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
