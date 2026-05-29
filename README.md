# ShipData: Structure et analyse des flottes maritimes

Projet de base de données - Printemps 2026
Groupe 04
Fatima Alame / Ramine Yunus / Gabriel Olivier Thorens / Anqi Liu / Matsvei Hamza / Kevin Nash Calegari

## 1. Description du projet

ShipData est une base de données relationnelle qui permet de stocker et d'interroger des informations sur des navires internationaux.

La base contient des données telles que :

- le numéro IMO du navire ;
- le nom du navire ;
- le type de navire ;
- l'année de construction ;
- le pavillon ;
- les caractéristiques techniques (comme le tonnage, la longueur, la largeur ou le tirant d'eau) ;
- la société de classification ;
- le constructeur ;
- le propriétaire ;
- les ports et les escales.

Le but du projet n'est pas seulement de stocker des données, mais aussi de pouvoir les interroger grâce à des requêtes SQL utiles pour analyser une flotte maritime. L'application permet par exemple de trouver les navires les plus anciens, de comparer les types de navires, de repérer les pavillons les plus fréquents, d'identifier les constructeurs les plus représentés ou encore de rechercher des navires selon plusieurs critères.

## 2. Utilisateurs possibles

L'application peut être utilisée par :

- des étudiants ou des chercheurs qui veulent analyser des données maritimes ;
- des analystes en logistique et en transport international ;
- des autorités portuaires ;
- des compagnies maritimes ;
- des personnes intéressées par les navires, leur origine, leur âge ou leur activité.

## 3. Structure générale de la base

La base est organisée en plusieurs tables afin d'éviter une seule grande table plate. L'objectif est de respecter une structure relationnelle claire et de limiter les redondances.

Tables principales du projet :

| Table | Rôle |
| --- | --- |
| `categorie_principale` | Stocke les grandes catégories de navires. |
| `type_navire` | Stocke les types précis de navires : cargo, navire-citerne (tanker), remorqueur (tug), navires à passager (passenger ship), etc. |
| `pavillon` | Stocke les pays de pavillon des navires. |
| `societe_classification` | Stocke les sociétés de classification. |
| `port` | Stocke les ports liés aux escales. |
| `constructeur` | Stocke les chantiers navals (builders). |
| `proprietaire` | Stocke les entreprises propriétaires des navires. |
| `navire` | Stocke les informations principales sur chaque navire. |
| `propriete_navire` | Stocke l'historique des propriétaires des navires. |
| `escale` | Stocke les arrivées et les départs des navires dans les ports. |

## 4. Technologies utilisées

- **PostgreSQL** : système de gestion de base de données relationnelle (SGBD).
- **SQL** : création, remplissage et interrogation de la base.
- **Python** : langage utilisé pour lancer l'interface.
- **Streamlit** : interface simple pour consulter et interroger la base.
- **Pandas** : affichage et manipulation des résultats SQL.
- **psycopg2-binary** : connexion entre Python et PostgreSQL.
- **Altair** : création de graphiques dans l'interface Streamlit.

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

### 5.2 Cloner le projet

Depuis le dossier racine du projet :

```bash
git clone https://github.com/fatimaalame/Shipdata/tree/main
cd Shipdata
```

### 5.3 Créer un environnement virtuel

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

Si PowerShell bloque l'activation de l'environnement virtuel, exécuter temporairement la commande suivante :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Puis relancer :

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5.4 Installer les librairies Python

Installer les dépendances à l'aide du fichier `requirements.txt` :

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

La création peut se faire via DBeaver, pgAdmin ou directement avec des lignes de commandes PostgreSQL.

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

| Fichier | Rôle |
| --- | --- |
| `01_create_tables.sql` | Crée les tables de la base. |
| `02_constraints.sql` | Ajoute les clés primaires, les clés étrangères, ainsi que les contraintes `UNIQUE` et les contraintes `CHECK`. |
| `03_insert_data.sql` | Indique l'ordre d'insertion des données depuis les fichiers CSV. |
| `04_nos_requetes.sql` | Contient les requêtes SQL principales du projet. |
| `05_drop_tables.sql` | Supprime les tables. Ce fichier doit uniquement être utilisé pour réinitialiser la base à zéro. |

Important : ne pas exécuter `05_drop_tables.sql`, sauf si l'objectif est de supprimer l'ensemble des tables existantes.

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
- `user` : votre nom d'utilisateur PostgreSQL ;
- `password` : votre mot de passe PostgreSQL ;
- `database` : le nom de votre base de donnés (ShipData).

Important : le fichier `config.json` contient un mot de passe local. Il ne doit pas être poussé sur GitHub.

Il est fortement recommandé d'ajouter cette ligne dans `.gitignore` :

```gitignore
config.json
```

## 8. Lancer l'interface

**Remarque importante** : la base de données « shipdata » et le fichier « config.json » doivent être configurés avant d’exécuter le programme !
Depuis la racine du projet, lancer la commande suivante :

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

- accéder à l'application en mode **visiteur** sans connexion ;
- se connecter avec différents rôles utilisateur : **propriétaire** ou **administrateur** ;
- afficher une page d'accueil personnalisée avec une image de fond et le logo ShipDATA ;
- naviguer avec une barre supérieure moderne contenant un menu utilisateur ;
- consulter la liste des navires sous forme de cartes détaillées ;
- rechercher un navire par nom, numéro IMO ou MMSI ;
- filtrer les navires par type ou par pavillon ;
- afficher des informations différentes selon le rôle connecté ;
- limiter certaines informations avancées aux propriétaires et aux administrateurs ;
- consulter des indicateurs simples : nombre de navires, pavillons, ports et sociétés de classification ;
- visualiser des graphiques simples sur les types de navires, pavillons, constructeurs et ports ;
- remplir une demande pour devenir propriétaire ;
- accéder à une page d'achat ou de demande d'ajout de bateau ;
- exporter les résultats en CSV pour les rôles autorisés ;
- exécuter des requêtes SQL prédéfinies pour les rôles avancés ;
- exécuter une requête `SELECT` personnalisée pour l'administrateur ;
- ajouter ou modifier certaines données de la base via le compte administrateur ;
- utiliser les fichiers CSV du dossier `02_DONNEES` comme données de secours si la base PostgreSQL n'est pas disponible.

## 10. Interface Streamlit

Le projet contient une interface web développée avec Streamlit. Elle se lance depuis le fichier principal :

```bash
python -m streamlit run .\07_RAPPORT_FINAL\streamlit_app.py
```

L'application utilise une base PostgreSQL configurée avec un fichier `config.json` placé à la racine du projet. Ce fichier doit contenir les informations de connexion locales de chaque utilisateur. Il ne doit pas être partagé directement sur GitHub, car le mot de passe peut être différent selon les ordinateurs.

Exemple de structure attendue :

```json
{
  "host": "localhost",
  "port": 5432,
  "user": "postgres",
  "password": "votre_mot_de_passe",
  "database": "shipdata"
}
```

Les fichiers CSV utilisés pour les données de secours ou l'importation doivent se trouver dans le dossier :

```text
02_DONNEES
```

L'interface contient maintenant plusieurs rôles :

- **Visiteur** : accès sans connexion, consultation simple des navires
- **Propriétaire** : accès avec compte, informations plus détaillées sur les navires
- **Administrateur** : accès complet, gestion des données et requêtes avancées

La page d'accueil utilise une image de fond et un logo stockés dans :

```text
07_RAPPORT_FINAL/INTERFACE
```

Le logo ShipDATA et l'image de fond doivent donc être conservés dans ce dossier pour que l'interface s'affiche correctement sur tous les ordinateurs.

L'interface permet notamment de consulter les navires sous forme de cartes, d'utiliser des filtres de recherche, d'accéder à des informations avancées selon le rôle connecté, et de remplir une demande pour devenir propriétaire. La gestion réelle des ajouts et modifications de données reste réservée au compte administrateur.

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
- Le fichier `config.json` ne doit ****jamais**** être envoyé sur GitHub.
- Les identifiants de connexion dans Streamlit sont des comptes de démonstration et ne constituent pas une authentification sécurisée pour une application réelle.
