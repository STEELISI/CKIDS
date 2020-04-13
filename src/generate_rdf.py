# # in creator.name:
# #   - replace . with " "
# #   - Split by , to get 1 author. Eg: Doe, John > John Doe, Copeland, Edwin Bingham -> Edwin Bingham Copeland
# #   - handle initials and "," and combine it to the same name. Eg: Conelin, G. E. -> G E Conelin
# #   - Split by , to get multiple authors. Eg: Nitin Arora1, Nikhil Srivastava2, Sai Sagar Peri3, Sumit Kumar4 & Alaknanda Ashok5
# #   - Split by &/and.. to get multiple authors with same affiliation
# #   - find and remove numbers. Eg: Sanjeev Kumar Dwivedi*1 and Ankur Singh Bist2 -> Sanjeev Kumar Dwivedi, Ankur Singh Bist
# #   - find and remove special characters. Eg: Sanjeev Kumar Dwivedi*1 -> Sanjeev Kumar Dwivedi
# #   - handle symbols in different languages. Eg: (Rivera, César), (Brandtzæg, Petter), (Krpo-Ćetković, Jasmina), (Radujković, Branko M.), (Šundić, Danijela)
# #   - remove Ms., Mrs., Mr. etc. 
# #     Keep Dr. etc.
# #   - handle multiple languages. Eg: डा ॅ0 भावना ग्रोवर दुआ
# #   - handle HTML tags in place of string
# #   - handle placeholder names. Eg: Ancient Indian and Tibetian scholars
# #   - handle NULL entries. Eg: &Na;, &Na;

# # to parse human names
# from nameparser import HumanName
# n = HumanName("Conelin, G. E.")
# # <HumanName : [
# # 	title: ''
# # 	first: 'G.'
# # 	middle: 'E.'
# # 	last: 'Conelin'
# # 	suffix: ''
# # 	nickname: ''
# # ]>

# # to parse organization addresses
# from postal.parser import parse_address
# parse_address('College of Cybersecurity, Sichuan University, Chengdu 610065, China')
# # [('college of cybersecurity sichuan university', 'house'), ('chengdu', 'city'), ('610065', 'postcode'), ('china', 'country')]

######################################################################################################################################################

from configparser import ConfigParser
import hashlib
import os
from pprint import pprint
import pymongo
from rdflib import URIRef, BNode, Literal, Namespace, Graph
from rdflib.namespace import RDF


cs = Namespace("https://w3id.org/cs/i/")
schema = Namespace("https://schema.org/")
g = Graph()

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


def add_content_links(an_hash, files):
    for f in files:
        g.add((cs[an_hash], schema.contentUrl, Literal(f["links"]["self"])))

def add_keywords(an_hash, keywords):
    kwrds = [j.strip() for i in keywords for j in i.split(",")]
    for kw in kwrds:
        g.add((cs[an_hash], schema.keywords, Literal(kw)))

def add_organization(org_name):
    org_hash = "o_" + str(int(hashlib.md5(org_name.encode('utf-8')).hexdigest(), 16))
    g.add((cs[org_hash], RDF.type, schema.Organization))
    g.add((cs[org_hash], schema.legalName, Literal(org_name)))
    return org_hash

def add_authors(an_hash, authors):
    for author in authors:
        name_hash = "p_" + str(int(hashlib.md5(author["name"].encode('utf-8')).hexdigest(), 16))
        g.add((cs[name_hash], RDF.type, schema.Person))
        g.add((cs[name_hash], schema.givenName, Literal(author["name"])))

        if "orcid" in author.keys():
            g.add((cs[name_hash], schema.identifier, Literal(author["orcid"])))

        if "affiliation" in author.keys():
            org_hash = add_organization(author["affiliation"])
            g.add((cs[name_hash], schema.affiliation, cs[org_hash]))
        
        g.add((cs[an_hash], schema.author, cs[name_hash]))

def add_software_triples(doc):
    artifact_name_hash = "a_" + str(int(hashlib.md5(doc["title"].encode('utf-8')).hexdigest(), 16))
    g.add((cs[artifact_name_hash], RDF.type, schema.SoftwareSourceCode))
    g.add((cs[artifact_name_hash], schema.name, Literal(doc["title"])))
    
    if "doi" in doc.keys():
        g.add((cs[artifact_name_hash], schema.identifier, Literal(doc["doi"])))
    if "created" in doc.keys():
        g.add((cs[artifact_name_hash], schema.datePublished, Literal(doc["created"])))
    if "description" in doc.keys():
        g.add((cs[artifact_name_hash], schema.description, Literal(doc["description"])))
    if "files" in doc.keys():
        add_content_links(artifact_name_hash, doc["files"])
    if "creators" in doc.keys():
        add_authors(artifact_name_hash, doc["creators"])
    if "keywords" in doc.keys():
        add_keywords(artifact_name_hash, doc["keywords"])

def add_dataset_triples(doc):
    artifact_name_hash = "a_" + str(int(hashlib.md5(doc["title"].encode('utf-8')).hexdigest(), 16))
    g.add((cs[artifact_name_hash], RDF.type, schema.Dataset))
    g.add((cs[artifact_name_hash], schema.name, Literal(doc["title"])))

    if "doi" in doc.keys():
        g.add((cs[artifact_name_hash], schema.identifier, Literal(doc["doi"])))
    if "created" in doc.keys():
        g.add((cs[artifact_name_hash], schema.datePublished, Literal(doc["created"])))
    if "description" in doc.keys():
        g.add((cs[artifact_name_hash], schema.description, Literal(doc["description"])))
    if "files" in doc.keys():
        add_content_links(artifact_name_hash, doc["files"])
    if "creators" in doc.keys():
        add_authors(artifact_name_hash, doc["creators"])
    if "keywords" in doc.keys():
        add_keywords(artifact_name_hash, doc["keywords"])

def add_publication_triples(doc):
    artifact_name_hash = "a_" + str(int(hashlib.md5(doc["title"].encode('utf-8')).hexdigest(), 16))
    g.add((cs[artifact_name_hash], RDF.type, schema.ScholarlyArticle))
    g.add((cs[artifact_name_hash], schema.headline, Literal(doc["title"])))

    if "doi" in doc.keys():
        g.add((cs[artifact_name_hash], schema.identifier, Literal(doc["doi"])))
    if "created" in doc.keys():
        g.add((cs[artifact_name_hash], schema.datePublished, Literal(doc["created"])))
    if "description" in doc.keys():
        g.add((cs[artifact_name_hash], schema.description, Literal(doc["description"])))
    if "files" in doc.keys():
        add_content_links(artifact_name_hash, doc["files"])
    if "creators" in doc.keys():
        add_authors(artifact_name_hash, doc["creators"])
    if "keywords" in doc.keys():
        add_keywords(artifact_name_hash, doc["keywords"])

def store_triples_to_file(graph):
    with open("../data/generated_rdf.ttl", "w") as f:
        f.write(g.serialize(format='turtle').decode("utf-8"))

if __name__ == "__main__":
    db = connect_to_db()
    docs = db["raw_artifacts"].find({"tfidf_score": {"$gt": 13}})
    count = 0
    for doc in docs:
        count += 1
        if doc["resource_type"]["type"] == "software":
            add_software_triples(doc)
        elif doc["resource_type"]["type"] == "dataset":
            add_dataset_triples(doc)
        elif doc["resource_type"]["type"] == "publication":
            add_publication_triples(doc)

    store_triples_to_file(g)
    print("Triples generated for {} artifacts.".format(count))