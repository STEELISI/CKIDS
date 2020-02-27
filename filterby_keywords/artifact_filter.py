import requests
from configparser import ConfigParser
import json
import pandas as pd
import re
import itertools
# Keyword Filter, to count the frequency of each keyword and get rid of the common keywords

config = ConfigParser()
config.read('secrets.ini')
API_ROOT = config['ZENODO_API']['API_ROOT']
ACCESS_KEY = config['ZENODO_API']['ACCESS_TOKEN']
df = pd.read_csv('v3_CKIDS_keywords_with_frequency.csv')

# Only search for kw that has frequency less than 500
kw = [row['Word'] for index, row in df.iterrows() if row['Frequency'] <= 500]

# Get combinations here
kw_combine = list(itertools.combinations(kw, 2))
kw_2grams = [k[0] + " " + k[1] for k in kw_combine]

# Get results with more than one keywords
with open('result.json', 'w') as f:
    for keyword in kw_2grams:
        # Set the params
        params = {
            "page": '1',
            "size": '500',
            'q': keyword,
            'access_token': ACCESS_KEY
        }
        # API call 
        res = requests.get(
            url=API_ROOT + 'records/', params=params)
        # To read the file data only
        data = res.json()["hits"]["hits"]

        # To do data clean here, need to know what kind of data and format we need







        # Duplicate reducing doing here, gonna store the artifact id for deduplicate







        f.write(json.dumps(data, indent=4))

f.close()