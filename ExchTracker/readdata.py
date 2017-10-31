import csv
with open('export-EtherPrice.csv', 'r') as f:
    reader = csv.reader(f)
    ethdata = list(reader)

print(len(ethdata))

action="BUY"
usd_amt=100.0
eth_amt=0.0
fee_percent=0.003
target_sell=0.00

for i in ethdata[150:160]:
    print(i)
    date=i[0]
    price=float(i[2])

    if action == "BUY":
        if price > 0.00:
            eth_amt = eth_amt + (usd_amt-(usd_amt*fee_percent))/price
            target_sell = price * 1.05
            usd_amt = 0.00
            action="SELL"
    print(date + " " + str(usd_amt) + " " + str(eth_amt)+ " "+ str(target_sell))
#    print(i[3])
