# CKIDS

## Project Description
**Goal**: To create a knowledge graph of cybersecurity artifacts mined from [Zenodo](https://www.zenodo.org)

Jelena's group has been working on collecting resources/artifacts that are important for cybersecurity. These resources are papers, datasets or software that are related to a cybersecurity topic. Jelena's student has been compiling the table she sent in a manual manner. We would like to speed up the process by identifying which resources in Zenodo are relevant to cybersecurity, their description and how do they relate together and build a knowledge graph allowing Jelena’s group to efficiently search for related artifacts.

## Data Collection
To collect data from Zenodo, we use the Zenodo API. The file ```scrape.py``` sends GET requests to the Zenodo API and stores the results as specified.

Required command-line arguments:
```shell script
python3 src/scrape.py -h
usage: scrape.py [-h] -k KEYWORD [KEYWORD ...] -s SIZE [-db]

optional arguments:
  -h, --help            show this help message and exit
  -k KEYWORD [KEYWORD ...], --keyword KEYWORD [KEYWORD ...]
                        keyword(s) to be searched in Zenodo
  -s SIZE, --size SIZE  number of query results to be requested from Zenodo
  -db, --db             (optional) stores collected data to MongoDB in the AWS
                        EC2 instance
```

Execution Examples:
```shell script
cd <PROJECT_ROOT>

# query with a single keyword, store results in JSON file
python3 src/scrape.py -k cybersecurity -s 100

# query with multiple keywords, store results in JSON file
python3 src/scrape.py -k cybersecurity vulnerability -s 100

# store results in MongoDB in the AWS EC2 instance
python3 src/scrape.py -k cybersecurity -s 100 -db
```

Expected Result: JSON document containing data for each artifact.
A sample of an artifact collected from Zenodo can be found in ```results/sample_artifact.json```

## Artifacts Storage Schema
When mining artifacts, the following information is saved:

* id: Zenodo URL/DOI.
* name: Title of the artifact
* type: whether it's a dataset, code or paper.
* abstract: abstract of the artifact
* author: Authors
* keywords: keywords used for describing the artifact.
* relatedTo: This will not be used for now, will be used to relate an artifact to a topic.

This is the schema which will be used to represent the data. Once we scrape some artifacts, then we can run topic modeling/clustering analysis to relate them by keyword.
