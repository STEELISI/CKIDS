# CKIDS
Project for creating a knowledge graph of cybersecurity artifacts mined from Zenodo

Jelena's group has been working on collecting resources/artifacts that are important for cybersecurity. These resources are papers, datasets or software that are related to a cybersecurity topic. Jelena's student has been compiling the table she sent in a manual manner. We would like to speed up the process by identifying which resources in Zenodo are relevant to cybersecurity, their description and how do they relate together and build a knowledge graph allowing Jelena’s group to efficiently search for related artifacts.

## Artefacts Format

The use case continues to be to retrieve Zenodo artifacts related to cybersecurity.

When mining artifacts, the following information is saved:

* id: Zenodo URL/DOI.
* name: Title of the artifact
* type: whether it's a dataset, code or paper.
* abstract: abstract of the artifact
* author: Authors
* keywords: keywords used for describing the artifact.
* relatedTo: This will not be used for now, will be used to relate an artifact to a topic.

This is the schema which will be used to represent the data. Once we scrape some artifacts, then we can run topic modeling/clustering analysis to relate them by keyword.
