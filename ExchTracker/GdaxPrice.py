import gdax
import json
public_client = gdax.PublicClient()

data = public_client.get_product_ticker(product_id='ETH-USD')

with open('.\output.txt', 'a') as file:
     file.write(json.dumps(data))
     file.write("\n")
