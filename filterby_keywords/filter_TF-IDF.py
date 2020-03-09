"""
Calculate Term Frequency and TF-IDF score for each unqiue keyword in 'v3_CKIDS_keywords_with_frequency.csv'
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pymongo
from configparser import ConfigParser
import json
import os
import requests


# mongodb configuration
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
# retreive description data
result = collection.find()
description_data = []
for obj in result:
    description_data += [obj['description']]
# remove empty description -- 834199 - 149 = 834050 descriptions
for d in description_data:
    if d == '':
        description_data.remove(d)
# brush keywords list
term_list = pd.read_csv('v3_CKIDS_keywords_with_frequency.csv', index_col=0)['Word'].unique()  # 194 - 4 = 190 unique words

# TF-IDF - sklearn
#vectorizer = TfidfVectorizer(vocabulary=set(term_list))
#X = vectorizer.fit_transform(description_data)
#pd.DataFrame({'Keyword':term_list, 'TFIDF_score':X.toarray().sum(axis=0)}).to_csv('kw_score_TFIDF.csv')

# TF-IDF - tf scheme - unary weighting IDF/no smoothing
def tf(term_list, documents):
    """
    Calculate term frequency for 'term'.
    
    input:
    ------
    term: the keyword to be evaluated.
    document: a document(here description paragraph string)
    
    output:
    -------
    a numerical frequency value.
    """
    N, T = len(documents), len(term_list)
    TF = np.zeros((N, T))
    for i in range(T):
        for j in range(N):
            TF[j, i] = documents[j].count(term_list[i])
    return TF

def idf(TF):
    """
    Calculate inverse document frequency for term wrt all documents.
    
    input:
    ------
    TF: term frequency, numpy array (#documents, #terms)
    
    output:
    -------
    numpy array (#terms), numerical values of idfs
    """
    N = TF.shape[0]
    return np.log(N/1+np.count_nonzero(TF, axis=0))

TF = tf(term_list, description_data)
IDF = idf(TF)
TFIDF = TF*IDF
pd.DataFrame({'Keyword':term_list, 'Term_frequency':TF.sum(axis=0), 'TFIDF_score':TFIDF.sum(axis=0)}).to_csv('kw_score_TF_TFIDF.csv')