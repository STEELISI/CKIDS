from bson.objectid import ObjectId
from collections import Counter
from configparser import ConfigParser
import json
import matplotlib.pyplot as plt
import numpy as np
from nltk.corpus import stopwords
import os
import pandas as pd
import pymongo
import re

def connect_to_db():
    config = ConfigParser()
    pardir = os.path.abspath(os.path.join(os.getcwd(), '..'))
    config.read(os.path.join(pardir, 'resources/secrets.ini'))

    DB_USER = config['MONGODB']['CKIDS_USER']
    DB_PASS = config['MONGODB']['CKIDS_PASS']
    DB_NAME = config['MONGODB']['CKIDS_DB_NAME']
    HOST = config['AWS']['HOST_IP']
    PORT = config['AWS']['HOST_PORT']

    # establish connection
    client = pymongo.MongoClient("mongodb://{DB_USER}:{DB_PASS}@{HOST}:{PORT}/{DB_NAME}".format(
        DB_USER=DB_USER, DB_PASS=DB_PASS, HOST=HOST, PORT=PORT, DB_NAME=DB_NAME))
    return client[DB_NAME]

def get_vocabulary():
    # with open("../data/vocab_with_priority.csv", "r") as f:
    with open("../data/keywords_with_priority_new_2.csv", "r") as f:
        data = f.readlines()[1:]
        vocab = {}
        for row in data:
            d = [i for i in row.strip().split(",")[1:] if i != ""]
            priority = int(d[0])
            for word in d[1:]:
                vocab[word.lower().replace("-", " ")] = priority
        return vocab

matched_words = {}
def get_score(words, vocabulary):
    local_matches = {}
    score = 0
    freq = Counter(words)
    for kwrd, priority in vocabulary.items():
        k = kwrd.split(" ")
        if all([word in words for word in k]):
            f = min([freq[word] for word in k])
            if kwrd in matched_words:
                matched_words[kwrd] += f
                local_matches[kwrd] += f
            else:
                matched_words[kwrd] = f
                local_matches[kwrd] = f
            score += (priority * f)
    return score, local_matches

if __name__ == "__main__":
    db = connect_to_db()
    docs = db["raw_artifacts"].find({"tfidf_score": {"$gt": 13}}).limit(5)
    # docs = db["raw_artifacts"].find({"_id": ObjectId("5e5fd5db6dc9c2e22610f3dd")})
    # print("#Documents with tf-idf score > 13 = ", str(db["raw_artifacts"].find({"tfidf_score": {"$gt": 13}}).count()))
    vocabulary = get_vocabulary()
    f = open("../results/sample_score_data.txt", "w")
    
    scores = dict()
    for doc in docs:
        # collect words to check
        text = doc["title"]
        if "description" in doc.keys():
            text += " " + doc["description"]
        if "keywords" in doc.keys():
            kwrds = [j.strip() for i in doc["keywords"] for j in i.split(",")]
            text += " ".join(kwrds)
        
        # preprocess
        pattern = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        cleantext = re.sub(pattern, '', text)
        cleantext = re.sub('\W+', ' ', cleantext)
        clean_list = cleantext.lower().split(" ")
        filtered_words = [word for word in clean_list if word not in stopwords.words('english')]
        # print(filtered_words)
        # print("\n")

        # calculate score
        score, matches = get_score(filtered_words, vocabulary)
        scores[doc["_id"]] = {
            "tf-idf score": doc["tfidf_score"],
            "New Score": score
        }
        
        # write to file
        f.write("\nObjectId: " + str(doc["_id"]) + "\n")
        f.write("tf-idf score: " + str(doc["tfidf_score"]) + "\n")
        f.write("New Relevance Score: " + str(score) + "\n")
        f.write("Matched Words with Frequency:\n" + json.dumps(matched_words, indent=4) + "\n")
        f.write("Title: " + doc["title"] + "\n")
        f.write("Artifact Type: " + doc["resource_type"]["type"] + "\n")
        f.write("\n" + "-" * 100 + "\n")
    
    df = pd.DataFrame.from_dict(scores, orient='index')
    df = df.sort_values('New Score', ascending=False)
    df = df.loc[(df['New Score'] > 0)]
    # print("#rows = ", str(df.shape[0]))

    print(json.dumps(matched_words, indent=4))
    # print(df)

    # with open('../results/words_with_freq_new_2.json', 'w') as fp:
    #     json.dump(matched_words, fp)
    # df.to_csv("../results/generated_scores_new_2.csv", sep=',', encoding='utf-8')

    # # plot histogram
    # plt.figure(figsize=[10,8])
    # n, bins, patches = plt.hist(x=df['New Score'], bins=list(range(0, 200, 5)), color='#0504aa',alpha=0.7, rwidth=0.85)
    # plt.grid(axis='y', alpha=0.75)
    # plt.xlabel('Score',fontsize=15)
    # plt.ylabel('#Documents',fontsize=15)
    # plt.xticks(fontsize=15)
    # plt.yticks(fontsize=15)
    # plt.title('Distribution of Scores over Documents',fontsize=15)
    # plt.show()
    