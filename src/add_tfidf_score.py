from bson.objectid import ObjectId
from configparser import ConfigParser
import json
import os
import pymongo

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

if __name__ == "__main__":
    db = connect_to_db()
    with open("../data/final_filter_TFIDF_result_new.json", "r") as f:
        data = json.load(f)
    print("{} documents".format(db.raw_artifacts.count_documents({})))
    count = 0
    for k, v in data.items():
        db.raw_artifacts.update_one({"_id": ObjectId(k)}, {"$set": {"tfidf_score_prob": v}})
        count += 1
        print("updated {} docs".format(count))
