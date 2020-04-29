import pymongo
import os
from configparser import ConfigParser
import requests

config = ConfigParser()
pardir = os.path.abspath(os.path.join(os.getcwd(), '..'))
config.read(os.path.join(pardir, 'resources/secrets.ini'))

# read API credentials
API_ROOT = config['CLOWDER_API']['API_ROOT']
ACCESS_KEY = config['CLOWDER_API']['ACCESS_TOKEN']
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': ACCESS_KEY
}

def create_dataset(title, description):
    """create_dataset creates an empty dataset with the title and description
    
    Parameters
    ----------
    title : String
        name of the artifact
    description : String
        description of the artifact
    
    Returns
    -------
    [String]
        ID of the dataset created on Clowder Hub
    """
    payload = {
        "name": title,
        "description": description,
        "access": "DEFAULT" # PUBLIC, PRIVATE, DEFAULT, TRIAL
    }

    res = requests.post(url=API_ROOT + '/datasets/createempty', headers=headers, json=payload)
    dataset_id = res.json()["id"]
    return dataset_id

def add_creators_to_dataset(d_id, creators):
    """add_creators_to_dataset adds each author to the specified artifact
    
    Parameters
    ----------
    d_id : String
        ID of the dataset
    creators : List
        names and affiliations of each author
    """
    for creator in creators:
        payload = { "creator": creator["name"] }
        res = requests.post(url=API_ROOT + '/datasets/{d_id}/creator'.format(d_id=d_id), headers=headers, json=payload)
        # print(res.text)

def add_tags_to_dataset(d_id, tags):
    """add_tags_to_dataset adds list of keywords to the specified artifact
    
    Parameters
    ----------
    d_id : String
        ID of the dataset
    tags : List
        strings of keywords
    """
    payload = { "tags": tags }
    res = requests.post(url=API_ROOT + '/datasets/{d_id}/tags'.format(d_id=d_id), headers=headers, json=payload)
    # print(res.text)

def add_metadata_to_dataset(d_id, created, files, resource_type):
    """add_metadata_to_dataset adds the following supporting metadata:
        - creation date and time
        - link(s) to download attachments (if any)
        - link(s) to downlaod code (if any)
    
    Parameters
    ----------
    d_id : String
        ID of the dataset
    created : String
        timestamp of the publication date
    files : List
        the URL links to each attachment
    resource_type : String
        specifies what kind of artifact is being uploaded. used to decide type of metadata
    """    
    payload = { "Date and Time": created }
    res = requests.post(url=API_ROOT + '/datasets/{d_id}/metadata'.format(d_id=d_id), headers=headers, json=payload)
    # print(res.text)

    if resource_type == "software":
        for url in files:
            payload = { "URL": url["links"]["self"] }
            res = requests.post(url=API_ROOT + '/datasets/{d_id}/metadata'.format(d_id=d_id), headers=headers, json=payload)
            # print(res.text)
    else:
        for url in files:
            payload = { "Code": url["links"]["self"] }
            res = requests.post(url=API_ROOT + '/datasets/{d_id}/metadata'.format(d_id=d_id), headers=headers, json=payload)
            # print(res.text)

def update_license_info(d_id):
    """update_license_info updates License information for the specified artifact
    
    Parameters
    ----------
    d_id : String
        ID of the dataset
    """    
    payload = {
        "licenseType": "Unknown",
        # "rightsHolder": "Unknown",
        # "licenseUrl": "",
        # "licenseText": "", # by-nc-nd, by-nd, by-nc, by-nc-sa, by-sa, by
        # "allowDownload": True
    }

    res = requests.post(url=API_ROOT + '/datasets/{d_id}/license'.format(d_id=d_id), headers=headers, json=payload)

if __name__ == "__main__":
    # read the database credentials
    DB_USER = config['MONGODB']['CKIDS_USER']
    DB_PASS = config['MONGODB']['CKIDS_PASS']
    DB_NAME = config['MONGODB']['CKIDS_DB_NAME']
    HOST = config['AWS']['HOST_IP']
    PORT = config['AWS']['HOST_PORT']

    # establish connection
    client = pymongo.MongoClient("mongodb://{DB_USER}:{DB_PASS}@{HOST}:{PORT}/{DB_NAME}".format(
        DB_USER=DB_USER, DB_PASS=DB_PASS, HOST=HOST, PORT=PORT, DB_NAME=DB_NAME))
    db = client[DB_NAME]

    # retreive documents
    documents = db["raw_artifacts"].find().limit(5)

    for doc in documents:
        # upload data using different API calls
        if "title" not in doc.keys() or "description" not in doc.keys():
            print("ID: {} - Artifact has no title and/or description".format(str(doc["_id"])))
            continue

        dataset_id = create_dataset(title=doc["title"], description=doc["description"])
        
        if "creators" in doc.keys():
            add_creators_to_dataset(dataset_id, doc["creators"])
        if "keywords" in doc.keys():
            add_tags_to_dataset(dataset_id, doc["keywords"])
        
        if "created" in doc.keys() or "files" in doc.keys():
            add_metadata_to_dataset(dataset_id, 
                created=doc["created"], 
                files=doc["files"],
                resource_type=doc["resource_type"]["type"]
                )

        # update_license_info(dataset_id)

        print("Success! See dataset at: https://hub.cyberexperimentation.org/datasets/"+dataset_id)