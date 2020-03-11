import requests
from configparser import ConfigParser
import json
import pandas as pd
import re
import itertools
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pymongo
import os
import requests
import collections

# count how many kws in one description, use brute force at the first
def count_kw(des):
    count = 0
    for kw in term_list:
        if kw in des:
            count += 1
    return count
# Setup DB connection
config = ConfigParser()
config.read('secrets.ini')
DB_USER = config['MONGODB']['CKIDS_USER']
DB_PASS = config['MONGODB']['CKIDS_PASS']
DB_NAME = config['MONGODB']['CKIDS_DB_NAME']
HOST = config['AWS']['HOST_IP']
PORT = config['AWS']['HOST_PORT']
# connect to mongodb
client = pymongo.MongoClient("mongodb://{DB_USER}:{DB_PASS}@{HOST}:{PORT}/{DB_NAME}".format(
    DB_USER=DB_USER, DB_PASS=DB_PASS, HOST=HOST, PORT=PORT, DB_NAME=DB_NAME))
db = client[DB_NAME]
collection = db["raw_artifacts"]
# retrieve raw data 
result = collection.find()

# def a used doi set
used = set()
frequency_list = []

# def the result dict
artifact_count = dict()
# brush keywords list
term_list = pd.read_csv('v3_CKIDS_keywords_with_frequency.csv', index_col=0)['Word'].unique()  


# store the results by DOI 
for obj in result:

    if obj.get("doi") and obj.get("doi") not in used:
        used.add(obj.get("doi"))
        temp_count = count_kw(obj['description'])
        if temp_count:
            artifact_count[obj.get("doi")]  = {}
            artifact_count[obj.get("doi")]["count"] = temp_count
            artifact_count[obj.get("doi")]['description'] = obj['description']
            frequency_list.append(temp_count)
    else:
        continue

# store CDF and artifact keywords count with description and doi
# For CDF: key is the frequency and value is count. For example: 
# [1, 18877] which means there are 18877 artifacts that have exactly one word in the their descriptions
with open("CDF.json", "w") as fp:
    json.dump(sorted(collections.Counter(frequency_list).items(), key = lambda x: x[0]), fp)
with open("artifact_count.json", "w") as fp:
    json.dump(sorted(artifact_count.items(), key=lambda x: x[1]["count"]), fp)

