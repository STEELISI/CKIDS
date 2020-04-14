"""
Calculate relevance score for each artifact in mongodb using TF-IDF score for each unqiue keyword in 'final_kw_list.csv'
"""
import pandas as pd
import numpy as np
import pymongo
from configparser import ConfigParser
import matplotlib.pyplot as plt
import json
import os
# from sklearn.feature_extraction.text import TfidfVectorizer

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
    term_list: the keyword to be evaluated, with options. np array, shape=(T, 2)
    documents: a list of strings (len=#entries)
    
    output:
    -------
    TF: numpy array shape=(#entries, #terms)
    """
    N, T = len(documents),len(term_list)
    TF = np.zeros((N, T))
    for j in range(N):
        d = documents[j].lower()
        for i in range(T):
            word_options = term_list[i]
            TF[j, i] = sum([d.count(w.lower()) for w in word_options])
    return TF
def idf(TF):
    """
    Calculate inverse document frequency for term wrt all documents.
    
    input:
    ------
    TF: term frequency, numpy array (#documents, #terms)
    
    output:
    -------
    numpy array (#terms), numerical values of idfs (probalistic IDF)
    """
    N = TF.shape[0]
    return np.log((N-np.count_nonzero(TF, axis=0))/(1+np.count_nonzero(TF, axis=0)))

# mongodb configuration
config = ConfigParser()
pardir = os.getcwd()
config.read(os.path.join(pardir, '../../resources/secrets.ini'))
DB_USER = config['MONGODB']['CKIDS_USER']
DB_PASS = config['MONGODB']['CKIDS_PASS']
DB_NAME = config['MONGODB']['CKIDS_DB_NAME']
HOST = config['AWS']['HOST_IP']
PORT = config['AWS']['HOST_PORT']
client = pymongo.MongoClient("mongodb://{DB_USER}:{DB_PASS}@{HOST}:{PORT}/{DB_NAME}".format(
    DB_USER=DB_USER, DB_PASS=DB_PASS, HOST=HOST, PORT=PORT, DB_NAME=DB_NAME))
db = client[DB_NAME]
collection = db["raw_artifacts"]
print("Connected to MongoDB.")
# retreive description data
result = collection.find()
objID_data = {}
for obj in result:
    description = obj['description']
    try:
        keywords = ' '.join(obj['keywords'])
    except KeyError:
        keywords = ''
        None
    title = obj['title']
    objID_data[obj['_id']] = title+' '+description+' '+keywords
print("Finished getting entries:", len(objID_data))
# Read in keywords directly
kw_csv = pd.read_csv('final_kw_list.csv', index_col=0)  # change filepath for other input file
term_list = list(kw_csv["Other_word_to_match"].str.split(', '))
print("Term list read.")
print("Calculating TF...")
TF = tf(term_list, list(objID_data.values()))
print("Calculating IDF...")
IDF = idf(TF)
print("Calculating TFIDF...")
TFIDF = TF*IDF
pd.DataFrame({'Keyword':[t[0].strip(' ') for t in term_list],
        'Term_frequency':TF.sum(axis=0),
        'TFIDF_score':TFIDF.sum(axis=0), 
        'Log_TFIDF_score':np.log(TFIDF.sum(axis=0)+1)}).to_csv('final_kw_TFIDF_Score.csv')
print("Finshed calculating weight scores for keywords.")
# Calculate entry scores
weight = pd.read_csv('final_kw_TFIDF_Score.csv', index_col=0)  # change filepath for other input file
kw_weights = dict(weight[['Keyword','TFIDF_score']].to_numpy())
log_doc_scores = np.log(TF@(weight['TFIDF_score'].to_numpy())+1)
doc_scores_result = dict(zip([str(k) for k in objID_data.keys()],log_doc_scores))
# plot CDF?
num_bins = 20  # change this for other #bins
counts, bin_edges = np.histogram(log_doc_scores, bins=num_bins)
cdf = np.cumsum(counts)/len(log_doc_scores)
plt.plot(bin_edges[1:], cdf)
plt.xlabel('Relevance Score')
plt.ylabel('cdf')
plt.title("CDF of Relevance Score with {0} bins".format(num_bins))
plt.savefig('rlv_score_cdf.png')
plt.show()
with open('final_filter_TFIDF_result.json', 'w') as f:   # change filepath for other output file
    json.dump(doc_scores_result, f)
print('Result saved in ', '"final_filter_TFIDF_result.json"')
