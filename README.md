# ShipData: Structure et analyse des flottes maritimes

Projet de base de données, Printemps 2026  
Groupe 04  
Fatima Alame / Ramine Yunus / Gabriel Olivier Thorens / Anqi Liu / Matsvei Hamza / Kevin Nash Calegari

## 1. Description du projet

ShipData est une base de données relationnelle qui permet de stocker et d'interroger des informations sur des navires internationaux.

La base contient des données comme :

- le numéro IMO du navire 
- le nom du navire 
- le type de navire 
- l'année de construction 
- le pavillon 
- les caractéristiques techniques comme le tonnage, la longueur, la largeur ou le tirant d'eau 
- la société de classification 
- le constructeur 
- le gestionnaire 
- le propriétaire 
- éventuellement les ports et les escales.

Le but n'est pas seulement de stocker des données, mais aussi de pouvoir les interroger avec des requêtes SQL utiles pour analyser une flotte maritime : trouver les navires les plus anciens, comparer les types de navires, repérer les pavillons les plus fréquents, identifier les constructeurs les plus représentés ou encore rechercher les navires selon plusieurs critères.

## 2. Utilisateurs possibles

L'application peut être utilisée par :

- des étudiants ou chercheurs qui veulent analyser des données maritimes 
- des analystes en logistique et transport international 
- des autorités portuaires 
- des compagnies maritimes 
- des personnes intéressées par les navires, leur origine, leur âge ou leur activité : ) 

## 3. Structure générale de la base

La base est organisée en plusieurs tables afin d'éviter une seule grande table plate. L'idée est de respecter une structure relationnelle claire et de limiter les redondances.

Tables principales prévues :

| Table | Rôle |
|---|---|
| `navire` | Stocke les informations principales sur chaque navire. |
| `type_navire` | Stocke les catégories de navires : cargo, tanker, tug, passenger ship, etc. |
| `pavillon` | Stocke les pays de pavillon des navires. |
| `port` | Stocke les ports liés aux escales. |
| `escale` | Stocke les arrivées et départs des navires dans les ports. |
| `societe_classification` | Stocke les sociétés de classification. |
| `constructeur` | Stocke les chantiers navals / builders. |
| `proprietaire` | Stocke les entreprises propriétaires des navires. |
| `gestionnaire` | Stocke les entreprises qui gèrent les navires, si cette table est présente dans la base. |

Selon l'implémentation finale, certains noms de tables ou de colonnes peuvent légèrement varier. L'interface Streamlit fournie est volontairement assez souple : elle inspecte automatiquement les tables et colonnes présentes dans PostgreSQL.

## 4. Technologies utilisées

- PostgreSQL : système de gestion de base de données relationnelle.
- SQL : création, remplissage et interrogation de la base.
- Python : langage utilisé pour lancer l'interface.
- Streamlit : interface simple pour consulter et interroger la base.
- Pandas : affichage et manipulation des résultats SQL.
- psycopg2-binary : connexion entre Python et PostgreSQL.

## 5. Installation

### 5.1 Installer Python

Installer Python 3 depuis le site officiel :

```bash
python --version
```

ou sur macOS :

```bash
python3 --version
```

### 5.2 Créer un environnement virtuel

Depuis le dossier du projet :

```bash
python -m venv .venv
```

Sur macOS / Linux :

```bash
source .venv/bin/activate
```

Sur Windows PowerShell :

```bash
.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'activation de l'environnement virtuel, lancer PowerShell en administrateur puis exécuter :

```bash
Set-ExecutionPolicy Unrestricted -Force
```

### 5.3 Installer les librairies Python

Avec un fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

Sinon, installer directement les librairies nécessaires :

```bash
pip install streamlit pandas psycopg2-binary
```

## 6. Création de la base de données

### 6.1 Créer la base PostgreSQL

Créer une base de données PostgreSQL nommée par exemple :

```text
shipdata
```

La création peut se faire dans DBeaver ou avec PostgreSQL directement.

### 6.2 Lancer le script SQL

Dans DBeaver :

1. Se connecter au serveur PostgreSQL.
2. Créer ou sélectionner la base `shipdata`.
3. Ouvrir le script SQL du projet, par exemple :

```text
sql/shipdata.sql
```

4. Exécuter le script pour créer les tables et insérer les données.

Le script doit contenir la création des tables, les clés primaires, les clés étrangères, les contraintes `NOT NULL`, `UNIQUE` et les données nécessaires pour tester les requêtes.

## 7. Configuration de la connexion postgreSQL

L’interface Streamlit utilise un fichier `config.json` placé à la racine du projet.

Créer un fichier `config.json` au même niveau que `README.md` avec le contenu suivant :

```json
{
  "host": "localhost",
  "port": 5432,
  "user": "postgres",
  "password": "votre_mot_de_passe_postgresql",
  "database": "shipdata"
}

À modifier selon votre installation PostgreSQL :

- `user` : votre utilisateur PostgreSQL ;
- `password` : votre mot de passe PostgreSQL ;
- `database` : le nom de votre base ShipData.

## 8. Lancer l'interface

Depuis le dossier du projet :

```bash
streamlit run interface_shipdata.py
```

Puis ouvrir le navigateur à l'adresse :

```text
http://localhost:8501/
```

## 9. Fonctionnalités de l'interface

L'interface permet de :

- vérifier la connexion à PostgreSQL 
- afficher les tables de la base 
- voir les colonnes détectées automatiquement 
- rechercher un navire par nom ou numéro IMO 
- filtrer les navires par type, pavillon, constructeur, propriétaire ou société de classification si ces colonnes existent 
- afficher des indicateurs simples : nombre de navires, tonnage moyen, âge moyen 
- visualiser des graphiques simples : navires par type, pavillon, constructeur ou société de classification 
- exécuter des requêtes SQL prédéfinies 
- écrire une requête "SELECT" personnalisée dans l'interface

## 10. Exemples de requêtes prévues

L'application peut servir à répondre à des questions comme :

1. Afficher tous les navires de la base
2. Rechercher un navire par numéro IMO
3. Afficher tous les navires construits avant 1995
4. Afficher les navires de plus de 30 ans
5. Lister les navires selon leur type
6. Trouver les navires battant pavillon d'un pays précis
7. Calculer l'âge moyen des navires par type
8. Trouver les navires ayant le plus grand tonnage
9. Afficher les navires classés par une société de classification donnée
10. Comparer le tonnage moyen selon le pavillon
11. Identifier les constructeurs ayant construit le plus de navires
12. Rechercher les propriétaires associés à plusieurs types de navires

## 11. Organisation du dossier

```text
ShipData/
├── README.md
├── config.json
├── interface_shipdata.py
├── requirements.txt
├── sql/
│   └── shipdata.sql
└── rapport/
    └── Rapport_ShipData.pdf
```

## 12. Remarques importantes

- Le projet doit être lancé avec une base PostgreSQL déjà créée et remplie.
- L'interface ne remplace pas le rapport : elle sert seulement à interroger la base.
- Les requêtes importantes doivent aussi être présentes dans le rapport final.
- Si une table ou une colonne n'apparaît pas dans l'interface, il faut vérifier que le script SQL a bien été exécuté dans la bonne base.
- Si la connexion échoue, il faut vérifier le fichier `config.json`, surtout le nom de la base, l'utilisateur et le mot de passe.
