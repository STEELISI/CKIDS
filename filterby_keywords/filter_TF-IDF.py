"""
Calculate Term Frequency and TF-IDF score for each unqiue keyword in 'v3_CKIDS_keywords_with_frequency.csv'
"""
import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pymongo
from configparser import ConfigParser


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
print("Connected to MongoDB.")
# retreive description data
result = collection.find()
description_data = []
keywords_data = []
title_data = []
for obj in result:
    if obj['description'] != '':
        description_data += [obj['description']]
    try:
        keywords_data += [' '.join(obj['keywords'])]
    except KeyError:
        None
    if obj['title'] != '':
        title_data += [obj['title']]
data = description_data + keywords_data + title_data
print("Finished getting all descriptions:", len(data),  # 2280318
    "\n", "#description:", len(description_data),  # 834050
    "\n", "#keywords:", len(keywords_data)),  # 612069
    "\n", "#title:", len(title_data))  # 834199

# old--brush keywords list
# keyword_data = pd.read_csv('v3_CKIDS_keywords_with_frequency.csv', index_col=0)
# def process_term_list(term_list):
#     term_list2 = []
#     for t in term_list:
#         # remove hyphens
#         if '-' in t:
#             term_list2 += [t.replace('-', ' ')]
#         # separate terms with brackets
#         elif "(" and ")" in t:
#             tt = t.split("(")
#             if tt[0] == '':
#                 term_list2 += [tt[1].replace(")","")]
#             term_list2 += [tt[0].rstrip(" "), tt[1].replace(")","")]
#         else:
#             term_list2 += [t]
#     return term_list2
# term_list = process_term_list(keyword_data['Word'].unique())
# term_list = set(term_list)
# term_list.discard('')
# term_list = sorted(list(term_list))

# updated--read in keywords directly
term_list = pd.read_csv('keywords_for_TFIDF.csv', index_col=0)['Keywords'].to_numpy()

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
            # match both 'ab-cd' and 'ab cd'
            if '-' in term_list[i]:
                word = term_list[i].replace('-', ' ')
                TF[j, i] = documents[j].lower().count(word.lower()) \
                            + documents[j].lower().count(term_list[i].lower())
            else:
                TF[j, i] = documents[j].lower().count(term_list[i].lower())
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

des_TF = tf(term_list, description_data)
des_IDF = idf(des_TF)
des_TFIDF = des_TF*des_IDF
pd.DataFrame({'Keyword':term_list, 'Term_frequency':des_TF.sum(axis=0), 'TFIDF_score':des_TFIDF.sum(axis=0)}).to_csv('kw_score_TF_TFIDF_description.csv')
TF = tf(term_list, data)
IDF = idf(TF)
TFIDF = TF*IDF
pd.DataFrame({'Keyword':term_list, 'Term_frequency':TF.sum(axis=0), 'TFIDF_score':TFIDF.sum(axis=0)}).to_csv('kw_score_TF_TFIDF_des_kw_ttl.csv')
print("Finshed.")