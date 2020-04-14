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

artimap = dict()


# Create a vector out of all keywords, from less frequent to more frequent. Each position will have a weight, which we can discuss.
kw = [row['Word'] for index, row in df.iterrows()]
weight = [1]*len(kw)
# Get combinations here
kw_combine = list(itertools.combinations(kw, 2))
kw_2grams = [k[0] + " " + k[1] for k in kw_combine]

# Have some trouble to connect ec2 database, here use the local data for test
with open('test.json') as f:
  testdata = json.load(f)
for wd, l in testdata.items():
    for artifact in l:
        if artifact.get("id"):
            print(artifact.get("id"))
            if artimap.get("id"):
                continue
            else:
                # Gonna add weight later
                count = 0
                if artifact.get("metadata").get("description"):
                    print(">")
                    for w in artifact["metadata"]["description"].split():
                        if w in kw:
                            count += 1
                artimap[artifact["id"]] = count
# Get the artifact dict with weight for each word = 1
print(artimap)

