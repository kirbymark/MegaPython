import gdax, json, csv
import os.path
import pendulum
import dateutil.parser

tz = pendulum.timezone('America/New_York')

public_client = gdax.PublicClient()


#get the data from GDAX API
data = public_client.get_product_ticker(product_id='ETH-USD')
data['nyc_time']= str(tz.convert(dateutil.parser.parse(data["time"])))


OutputFile='output2.csv'

file_exists = os.path.isfile(OutputFile)

with open(OutputFile, 'a+') as f:  # Just use 'w' mode in 3.x
    w = csv.writer(f,delimiter=',')
    if not file_exists:
        w.writerow(data.keys())
    w.writerow(data.values())
