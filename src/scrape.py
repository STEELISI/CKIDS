import requests
from configparser import ConfigParser
import json

config = ConfigParser()
config.read('secrets.ini')
API_ROOT = config['ZENODO_API']['API_ROOT']
ACCESS_KEY = config['ZENODO_API']['ACCESS_TOKEN']
params = {
    'page': '1',
    'size': '2000',             # set max. number of search results
    'q': 'cybersecurity',       # add vocabulary keywords here
    'access_token': ACCESS_KEY
}

res = requests.get(url=API_ROOT + 'records/', params=params)

with open('result.json', 'w') as f:
    data = res.json()
    f.write(json.dumps(data, indent=4))
