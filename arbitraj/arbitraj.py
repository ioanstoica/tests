from dotenv import load_dotenv
load_dotenv()

import os
import requests
import json

# request all prices for BTC-USD
response = requests.get('https://api.pro.coinbase.com/products/BTC-USD/ticker')
text = json.loads(response.text)

print(text)






