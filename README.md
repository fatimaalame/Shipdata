# ShipData: Structure et analyse des flottes maritimes

Projet de base de données, Printemps 2026  
Groupe 04  
Fatima Alame / Ramine Yunus / Gabriel Olivier Thorens / Anqi Liu / Matsvei Hamza / Kevin Nash Calegari

## 1. Description du projet

ShipData est une base de données relationnelle qui permet de stocker et d'interroger des informations sur des navires internationaux.

La base contient des données comme :

- le numéro IMO du navire ;
- le nom du navire ;
- le type de navire ;
- l'année de construction ;
- le pavillon ;
- les caractéristiques techniques comme le tonnage, la longueur, la largeur ou le tirant d'eau ;
- la société de classification ;
- le constructeur ;
- le propriétaire ;
- les ports et les escales.

Le but du projet n'est pas seulement de stocker des données, mais aussi de pouvoir les interroger avec des requêtes SQL utiles pour analyser une flotte maritime. L'application permet par exemple de trouver les navires les plus anciens, de comparer les types de navires, de repérer les pavillons les plus fréquents, d'identifier les constructeurs les plus représentés ou encore de rechercher des navires selon plusieurs critères.

## 2. Utilisateurs possibles

L'application peut être utilisée par :

- des étudiants ou chercheurs qui veulent analyser des données maritimes ;
- des analystes en logistique et transport international ;
- des autorités portuaires ;
- des compagnies maritimes ;
- des personnes intéressées par les navires, leur origine, leur âge ou leur activité.

## 3. Structure générale de la base

La base est organisée en plusieurs tables afin d'éviter une seule grande table plate. L'objectif est de respecter une structure relationnelle claire et de limiter les redondances.

Tables principales du projet :

| Table | Rôle |
| --- | --- |
| `categorie_principale` | Stocke les grandes catégories de navires. |
| `type_navire` | Stocke les types précis de navires : cargo, tanker, tug, passenger ship, etc. |
| `pavillon` | Stocke les pays de pavillon des navires. |
| `societe_classification` | Stocke les sociétés de classification. |
| `port` | Stocke les ports liés aux escales. |
| `constructeur` | Stocke les chantiers navals / builders. |
| `proprietaire` | Stocke les entreprises propriétaires des navires. |
| `navire` | Stocke les informations principales sur chaque navire. |
| `propriete_navire` | Stocke l'historique des propriétaires des navires. |
| `escale` | Stocke les arrivées et départs des navires dans les ports. |

## 4. Technologies utilisées

- PostgreSQL : système de gestion de base de données relationnelle.
- SQL : création, remplissage et interrogation de la base.
- Python : langage utilisé pour lancer l'interface.
- Streamlit : interface simple pour consulter et interroger la base.
- Pandas : affichage et manipulation des résultats SQL.
- psycopg2-binary : connexion entre Python et PostgreSQL.
- Altair : création de graphiques dans l'interface Streamlit.

## 5. Installation

### 5.1 Installer Python

Installer Python 3 depuis le site officiel, puis vérifier l'installation avec :

```bash
python --version
```

Sur macOS ou Linux, la commande peut aussi être :

```bash
python3 --version
```

### 5.2 Créer un environnement virtuel

Depuis le dossier racine du projet :

```bash
python -m venv .venv
```

Sur macOS ou Linux :

```bash
source .venv/bin/activate
```

Sur Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'activation de l'environnement virtuel, exécuter temporairement :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Puis relancer :

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5.3 Installer les librairies Python

Avec le fichier `requirements.txt` :

```bash
pip install -r requirements.txt
```

Le fichier `requirements.txt` doit contenir :

```text
streamlit
pandas
psycopg2-binary
altair
```

## 6. Création de la base de données

### 6.1 Créer la base PostgreSQL

Créer une base de données PostgreSQL nommée par exemple :

```text
shipdata
```

La création peut se faire dans DBeaver, pgAdmin ou directement avec PostgreSQL.

Dans DBeaver, il est possible de créer la base avec la commande suivante :

```sql
CREATE DATABASE shipdata;
```

### 6.2 Lancer les scripts SQL

Les scripts SQL du projet se trouvent dans le dossier :

```text
05_SQL/
```

Dans DBeaver :

1. Se connecter au serveur PostgreSQL.
2. Créer ou sélectionner la base `shipdata`.
3. Ouvrir les scripts SQL du dossier `05_SQL`.
4. Exécuter les scripts dans l'ordre suivant :

```text
01_create_tables.sql
02_constraints.sql
03_insert_data.sql
```

Le rôle des fichiers est le suivant :

| Fichier                | Rôle |
|------------------------| --- |
| `01_create_tables.sql` | Crée les tables de la base. |
| `02_constraints.sql`   | Ajoute les clés primaires, les clés étrangères, les contraintes `UNIQUE` et les contraintes `CHECK`. |
| `03_insert_data.sql`   | Indique l'ordre d'insertion des données depuis les fichiers CSV. |
| `04_nos_requetes.sql`  | Contient les requêtes SQL principales du projet. |
| `05_drop_tables.sql`   | Supprime les tables. Ce fichier doit seulement être utilisé pour recommencer la base à zéro. |

Important : ne pas exécuter `05_drop_tables.sql`, sauf si l'objectif est de supprimer les tables existantes.

## 7. Configuration de la connexion PostgreSQL

L'interface Streamlit utilise un fichier `config.json` placé à la racine du projet.

Créer un fichier `config.json` au même niveau que `README.md` avec le contenu suivant :

```json
{
  "host": "localhost",
  "port": 5432,
  "user": "postgres",
  "password": "votre_mot_de_passe_postgresql",
  "database": "shipdata"
}
```

À modifier selon votre installation PostgreSQL :

- `host` : généralement `localhost` si la base est sur votre ordinateur ;
- `port` : généralement `5432` pour PostgreSQL ;
- `user` : votre utilisateur PostgreSQL ;
- `password` : votre mot de passe PostgreSQL ;
- `database` : le nom de votre base ShipData.

Important : le fichier `config.json` contient un mot de passe local. Il ne doit pas être envoyé sur GitHub.

Il est recommandé d'ajouter cette ligne dans `.gitignore` :

```gitignore
config.json
```

## 8. Lancer l'interface

Depuis la racine du projet, lancer la commande suivante : 
Remarque importante : la base de données « shipdata » et le fichier « config.json » doivent être configurés avant d’exécuter le programme !

```bash
python -m streamlit run ./07_RAPPORT_FINAL/streamlit_app.py
```

Sur Windows PowerShell, la commande peut aussi s'écrire :

```powershell
python -m streamlit run .\07_RAPPORT_FINAL\streamlit_app.py
```

Puis ouvrir le navigateur à l'adresse :

```text
http://localhost:8501/
```

## 9. Fonctionnalités de l'interface

L'interface permet de :

- se connecter avec un rôle utilisateur ;
- vérifier la connexion à PostgreSQL ;
- rechercher un navire par nom, numéro IMO ou MMSI ;
- filtrer les navires par type, pavillon ou société de classification ;
- afficher des indicateurs simples : nombre de navires, nombre de pavillons, nombre de ports et nombre de sociétés de classification ;
- afficher les résultats dans un tableau lisible ;
- visualiser des graphiques simples ;
- exécuter des requêtes SQL prédéfinies ;
- exporter les résultats en CSV pour certains rôles ;
- exécuter une requête `SELECT` personnalisée pour l'administrateur ;
- afficher la structure détectée de la base pour l'administrateur.

## 10. Gestion des rôles utilisateur dans l'interface

L'interface Streamlit inclut un système de connexion simple permettant d'afficher des informations différentes selon le type d'utilisateur connecté. Cette fonctionnalité sert à simuler plusieurs niveaux d'accès dans l'application.

Les comptes sont des comptes de démonstration définis directement dans le fichier `streamlit_app.py`. Ils ne doivent pas être considérés comme un système d'authentification sécurisé pour une application réelle, mais ils permettent de montrer comment l'interface peut adapter les données affichées selon le rôle de l'utilisateur.

### 10.1 Comptes disponibles

| Identifiant | Mot de passe | Rôle affiché |
| --- | --- | --- |
| `client` | `client123` | Client |
| `capitaine` | `capitaine123` | Employé / capitaine |
| `employe` | `employe123` | Employé / capitaine |
| `admin` | `admin123` | Administrateur |

### 10.2 Rôle Client

Le rôle `Client` correspond à un utilisateur externe qui consulte seulement les informations principales sur les navires.

Le client peut voir :

- le tableau de bord général ;
- les métriques principales ;
- la recherche simple de navires ;
- les statistiques générales ;
- les informations publiques des navires : IMO, nom du navire, type, année de construction, pavillon et longueur.

Le client ne peut pas voir :

- les requêtes SQL prédéfinies ;
- la requête SQL personnalisée ;
- la structure détectée de la base ;
- l'export CSV ;
- les données plus techniques comme le MMSI, le GT, le DWT, le constructeur ou le propriétaire actuel.

### 10.3 Rôle Employé / capitaine

Le rôle `Employé / capitaine` correspond à un utilisateur interne qui a besoin de consulter des informations plus détaillées pour l'analyse ou le suivi opérationnel.

L'employé ou capitaine peut voir :

- le tableau de bord général ;
- la recherche avancée ;
- les filtres par type de navire, pavillon et société de classification ;
- les informations détaillées des navires : IMO, MMSI, nom, type, année, pavillon, GT, DWT, longueur, classification et propriétaire actuel ;
- l'export CSV des résultats ;
- les graphiques supplémentaires ;
- les requêtes SQL prédéfinies du projet.

L'employé ou capitaine ne peut pas voir :

- la requête SQL personnalisée ;
- la structure détectée de la base ;
- les informations de diagnostic réservées à l'administrateur.

Dans cette version de l'application, les comptes `capitaine` et `employe` ont les mêmes droits. Ils sont séparés uniquement pour représenter deux profils possibles d'utilisateurs internes.

### 10.4 Rôle Administrateur

Le rôle `Administrateur` correspond à l'utilisateur ayant l'accès le plus complet à l'interface.

L'administrateur peut voir :

- le tableau de bord général ;
- la recherche avancée complète ;
- toutes les colonnes disponibles dans les résultats ;
- les informations techniques comme la largeur, le tirant d'eau, le constructeur et le propriétaire actuel ;
- l'export CSV ;
- tous les graphiques ;
- toutes les requêtes SQL prédéfinies ;
- la requête SQL personnalisée ;
- la structure détectée de la base PostgreSQL.

La requête SQL personnalisée est limitée aux requêtes de lecture. L'interface autorise uniquement les requêtes commençant par `SELECT` ou `WITH`. Les commandes pouvant modifier ou supprimer les données, comme `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE` ou `TRUNCATE`, sont bloquées.

### 10.5 Résumé des droits

| Fonctionnalité | Client | Employé / capitaine | Administrateur |
| --- | ---: | ---: | ---: |
| Connexion à l'interface | Oui | Oui | Oui |
| Tableau de bord général | Oui | Oui | Oui |
| Recherche de navires | Oui | Oui | Oui |
| Filtres avancés | Partiel | Oui | Oui |
| Affichage des données publiques | Oui | Oui | Oui |
| Affichage des données techniques | Non | Partiel | Oui |
| Export CSV | Non | Oui | Oui |
| Graphiques statistiques | Oui | Oui | Oui |
| Requêtes SQL prédéfinies | Non | Oui | Oui |
| Requête SQL personnalisée | Non | Non | Oui |
| Structure détectée de la base | Non | Non | Oui |

## 11. Exemples de requêtes prévues

L'application peut servir à répondre à des questions comme :

1. Afficher tous les navires de la base.
2. Rechercher un navire par numéro IMO.
3. Afficher tous les navires construits avant 1995.
4. Afficher les navires de plus de 30 ans.
5. Lister les navires selon leur type.
6. Trouver les navires battant pavillon d'un pays précis.
7. Calculer l'âge moyen des navires par type.
8. Trouver les navires ayant le plus grand tonnage.
9. Afficher les navires classés par une société de classification donnée.
10. Comparer le tonnage moyen selon le pavillon.
11. Identifier les constructeurs ayant construit le plus de navires.
12. Rechercher les propriétaires associés à plusieurs types de navires.
13. Afficher les ports ayant le plus d'escales.
14. Consulter l'historique des propriétaires d'un navire.

## 12. Organisation du dossier

Structure simplifiée du projet :

```text
ShipData/
├── README.md
├── requirements.txt
├── config.json                    # à créer localement, ne pas envoyer sur GitHub
├── 00_ADMIN/
├── 01_RESSOURCES/
├── 02_DONNEES/
├── 03_MODELE_BDD/
├── 05_SQL/
│   ├── 01_create_tables.sql
│   ├── 02_constraints.sql
│   ├── 03_insert_data.sql
│   ├── 04_nos_requetes.sql
│   ├── 05_views.sql
│   └── 06_drop_tables.sql
├── 05_SCRIPTS_sep/
└── 07_RAPPORT_FINAL/
    └── streamlit_app.py
```

## 13. Remarques importantes

- Le projet doit être lancé avec une base PostgreSQL déjà créée et remplie.
- L'interface ne remplace pas le rapport : elle sert à interroger la base et à visualiser les résultats.
- Les requêtes importantes doivent aussi être présentes dans le rapport final.
- Si une table ou une colonne n'apparaît pas dans l'interface, il faut vérifier que les scripts SQL ont bien été exécutés dans la bonne base.
- Si la connexion échoue, il faut vérifier le fichier `config.json`, surtout le nom de la base, l'utilisateur et le mot de passe.
- Le fichier `config.json` ne doit pas être envoyé sur GitHub.
- Les identifiants de connexion dans Streamlit sont des comptes de démonstration et ne constituent pas une authentification sécurisée pour une application réelle.
