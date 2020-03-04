import argparse
from configparser import ConfigParser
import json
import os
import pymongo
import requests

config = ConfigParser()
pardir = os.getcwd()
config.read(os.path.join(pardir, 'resources/secrets.ini'))


def get_artifacts_zenodo(keyword, page):
    """
    sends a GET request to Zenodo and retrieves artifacts based on search keywords and number of results

    :param keyword: List
        A list of strings to search based on (vocabulary)
    :param size: str
        A number entered as a string to request a fixed number of search results
    :return: dict
        a JSON document with the response data or None
    """
    API_ROOT = config['ZENODO_API']['API_ROOT']
    ACCESS_KEY = config['ZENODO_API']['ACCESS_TOKEN']

    params = {
        'page': page,
        'q': keyword,
        'size': '1000',
        'access_token': ACCESS_KEY
    }

    try:
        res = requests.get(url=API_ROOT + 'records/', params=params)
    except requests.exceptions.ConnectionError as conn_err:
        print(conn_err)
        return None
    except requests.exceptions.HTTPError as http_err:
        print(http_err)
        return None

    return dict(res.json())


def insert_into_db(db, data):
    """
    inserts JSON documents into MongoDB

    :param data: list
        a collection of JSON documents (as a dict) for each artifact
    :return: success status of insertion(s)
    """
    # print('connection established')
    filtered_data = []
    for document in data:
        # insert only the necessary columns
        doc_structure = {}
        if "doi" in document:
            doc_structure["doi"] = document["doi"]
        if "created" in document:
            doc_structure["created"] = document["created"]
        if "files" in document:
            doc_structure["files"] = document["files"]
        if "title" in document["metadata"]:
            doc_structure["title"] = document["metadata"]["title"]
        if "creators" in document["metadata"]:
            doc_structure["creators"] = document["metadata"]["creators"]
        if "description" in document["metadata"]:
            doc_structure["description"] = document["metadata"]["description"]
        if "keywords" in document["metadata"]:
            doc_structure["keywords"] = document["metadata"]["keywords"]
        if "resource_type" in document["metadata"]:
            doc_structure["resource_type"] = document["metadata"]["resource_type"]
        filtered_data.append(doc_structure)

    insert_id = db["raw_artifacts"].insert_many(filtered_data)


def main():
    # read command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keyword",
                        nargs='+',
                        help="keyword(s) to be searched in Zenodo",
                        required=False)
    parser.add_argument("-s", "--size",
                        help='number of query results to be requested from Zenodo',
                        required=False)
    parser.add_argument("-db", "--db",
                        help="(optional) stores collected data to MongoDB in the AWS EC2 instance",
                        action='store_true')
    args = parser.parse_args()

    # get artifacts from Zenodo
    with open(os.path.join(pardir, 'resources/v2_CKIDS_keywords.csv'), 'r') as inf:
        keywords = [x.strip() for x in inf.readlines()]
    
    DB_USER = config['MONGODB']['CKIDS_USER']
    DB_PASS = config['MONGODB']['CKIDS_PASS']
    DB_NAME = config['MONGODB']['CKIDS_DB_NAME']
    HOST = config['AWS']['HOST_IP']
    PORT = config['AWS']['HOST_PORT']

    client = pymongo.MongoClient("mongodb://{DB_USER}:{DB_PASS}@{HOST}:{PORT}/{DB_NAME}".format(
        DB_USER=DB_USER, DB_PASS=DB_PASS, HOST=HOST, PORT=PORT, DB_NAME=DB_NAME))
    db = client[DB_NAME]
    
    for keyword in keywords:
        size = get_artifacts_zenodo(keyword, '1')['hits']['total']
        num_pages = max(round(size/1000), 1)
        print("Total hits on {} = {}".format(keyword, size))
        for i in range(1, num_pages+1):
            data = get_artifacts_zenodo(keyword, str(i))
            print('\tStoring page {} in db'.format(i))

            # write results into a database
            if args.db:
                insert_into_db(db, data['hits']['hits'])
            # write results into a JSON file
            else:
                with open(os.path.join(pardir, 'results/zenodo_artifacts_dump.json'), 'a') as f_ptr:
                    f_ptr.write(json.dumps(data, indent=4))
    
        print('Count of documents = ' + str(db.raw_artifacts.count_documents({})))

    client.close()


if __name__ == '__main__':
    main()
