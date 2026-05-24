# ShipData (groupe 04)

ShipData est un projet de base de données réalisé dans le cadre du cours de Bases de données à l’Université de Genève.

Le projet porte sur le domaine du transport maritime. Il vise à construire une base de données relationnelle permettant de stocker et d’interroger des informations sur des navires, leurs types, leurs pavillons, leurs sociétés de classification, leurs constructeurs, leurs propriétaires, ainsi que leurs escales dans différents ports.

La base contient des données réelles nettoyées lorsque c’était possible, complétées par des données fictives réalistes afin d’obtenir un ensemble cohérent et exploitable pour les requêtes SQL du projet.

## Objectif du projet

L’objectif est de concevoir, créer et interroger une base de données relationnelle en PostgreSQL.

La base doit permettre de répondre à des questions comme :

- quels navires appartiennent à un type donné 
- quels pavillons sont les plus fréquents 
- quels constructeurs ont construit le plus de navires 
- quels ports ont été visités par un navire 
- quels propriétaires ont possédé un navire sur une période donnée 
- quelles escales ont eu lieu dans un port précis 
- etc...

## Structure du projet (en construction...)

```text
ShipData/
├── Data/
│   ├── 01_categorie_principale.csv
│   ├── 02_type_navires.csv
│   ├── 03_pavillons.csv
│   ├── 04_societes_classification.csv
│   ├── 05_port_data.csv
│   ├── 06_constructeurs.csv
│   ├── 07_proprietaires.csv
│   ├── 08_navires.csv
│   ├── 09_propriete_navire.csv
│   └── 10_escales.csv
├── Documentation/
├── Rapport/
│   ├── images/
│   ├── DescriptionGenerale.md
│   └── rapport.md
├── SQL/
│   ├── 01_create_tables.sql
│   ├── 02_constraints.sql
│   ├── 03_insert_data.sql
│   ├── 04_queries.sql
│   └── 05_views.sql
├── README.md
├── requirements.txt
└── streamlit_app.py


### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
