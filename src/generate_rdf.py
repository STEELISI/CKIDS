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
db = client[DB_NAME]


cs = Namespace("https://w3id.org/cs/i/")
schema = Namespace("https://schema.org/")
g = Graph()


docs = db["raw_artifacts"].find().limit(5)

for doc in docs:
    pprint(doc)

    # Artifact Type: Software
    if doc["resource_type"]["type"] == "software":
        artifact_name_hash = "a_" + str(int(hashlib.md5(doc["title"].encode('utf-8')).hexdigest(), 16))
        g.add((cs[artifact_name_hash], RDF.type, schema.SoftwareSourceCode))
        g.add((cs[artifact_name_hash], schema.identifier, Literal(doc["doi"])))
        g.add((cs[artifact_name_hash], schema.datePublished, Literal(doc["created"])))
        g.add((cs[artifact_name_hash], schema.name, Literal(doc["title"])))
        g.add((cs[artifact_name_hash], schema.description, Literal(doc["description"])))

        if "files" in doc.keys():
            for f in doc["files"]:
                g.add((cs[artifact_name_hash], schema.contentUrl, Literal(f["links"]["self"])))
        
        if "keywords" in doc.keys():
            keywords = [j.strip() for i in doc["keywords"] for j in i.split(",")]
            for keyword in keywords:
                g.add((cs[artifact_name_hash], schema.keywords, Literal(keyword)))

        if "creators" in doc.keys():
            # create author and org triples
            for creator in doc["creators"]:
                name_hash = "p_" + str(int(hashlib.md5(creator["name"].encode('utf-8')).hexdigest(), 16))
                g.add((cs[name_hash], RDF.type, schema.Person))
                g.add((cs[name_hash], schema.givenName, Literal(creator["name"])))

                if "orcid" in creator.keys():
                    g.add((cs[name_hash], schema.identifier, Literal(creator["orcid"])))

                if "affiliation" in creator.keys():
                    org_hash = "o_" + str(int(hashlib.md5(creator["affiliation"].encode('utf-8')).hexdigest(), 16))
                    g.add((cs[org_hash], RDF.type, schema.Organization))
                    g.add((cs[org_hash], schema.legalName, Literal(creator["affiliation"])))
                    g.add((cs[name_hash], schema.affiliation, cs[org_hash]))
                
                g.add((cs[artifact_name_hash], schema.author, cs[name_hash]))

with open("../data/generated_rdf.ttl", "w") as f:
    f.write(g.serialize(format='turtle').decode("utf-8"))















































