# Humans-in-the-Loop (HITL)

HITL aims to model, test, and evaluate various relationships and interactions between crowdsourcing and machine learning methods in ways that will expand the Library of Congress' existing efforts to ethically enhance usability, discovery, and user engagement around digital collections.  

The HITL initiative encompasses machine learning and crowdsourcing prototypes, proof-of-concept experiments, reports, and accompanying recommendations that deepen LC Labs’ exploration of the opportunities and challenges that come from operationalizing emerging technologies at scale.   

Between September 2020 and June 2021, [AVP](https://weareavp.com) worked with LC Labs to develop a framework for designing “human-in-the-loop” data enrichment projects that are engaging, ethical, and useful, which was delivered as part of a recommendations report in July 2021. This repository contains the data, code, and other design and development artifacts of the project.  

Contents include:
- _crowdsourcing-data-flow-scripts:_ Python scripts for managing data flow between Scribe and the workflow database
- _machine-learning-scripts:_ Python scripts for initializing the PostgreSQL workflow database and running the machine learning pipeline
- _sample-output-data:_ sample structured data for business listings and Python code for generating it from the workflow database
- _scribe-hitl:_ a version of the Scribe platform customized for the project
- _workflow-database:_ documentation and initialization scripts for the workflow database

READMEs within each folder give more detail on each.  

### AVP project team
- __Shawn Averkamp__, Project Lead, Subject Matter Expert
- __Kerri Willette__, User Testing Lead, Subject Matter Expert
- __Amy Rudersdorf__, Project Manager, Subject Matter Expert
- __Dan Fischer__, Machine Learning Expert, Software Engineer
- __Casey Arendt__, UI/UX Designer for Presentation Interface
- __Wes Doyle__, Software Engineer