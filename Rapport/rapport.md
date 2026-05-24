## Description générale du projet

ShipData est une base de données relationnelle dédiée au transport maritime. L'idée de départ était simple: ce domaine est extrêmement structuré dans la réalité, chaque navire a un identifiant unique (le numéro IMO), un pavillon, un ou plusieurs propriétaires au fil du temps, un constructeur, une société qui le certifie, et une histoire de déplacements à travers les ports du monde. Il nous a  donc semblé naturel d'en faire le sujet de notre projet.

La base stocke des informations sur 45 navires, répartis en 12 types regroupés en 8 catégories principales (vraquiers, porte-conteneurs, pétroliers, navires de croisière, etc…). Pour chaque navire, on retrouve ses caractéristiques techniques (tonnage, dimensions, tirant d'eau) ainsi que son pavillon d'immatriculation parmi 114 pays, sa société de classification parmi 20 organismes internationaux, et son chantier naval parmi 18 constructeurs. L'historique de propriété est représenté dans une table dédiée, ce qui permet de suivre les transferts de propriété d'un navire dans le temps. Et enfin, 96 escales dans 110 ports répartis dans le monde permettent d'analyser les déplacements et l'activité des navires.

L'usage principal de ShipData est la consultation et l'analyse de données maritimes. On peut par exemple identifier les pavillons les plus représentés dans la flotte, comparer les navires selon leur tonnage ou leurs dimensions, retrouver les ports les plus fréquentés, suivre l'historique de propriété d'un navire particulier, ou encore analyser les escales par type de port ou par région (qu’on démontrera à l’aide des requêtes SQL). La base transforme ainsi des données dispersées en informations lisibles et exploitables, de manière à ce que ce soit accessible pour tous.

En parlant des utilisateurs, les cibles sont variées. On pourrait avoir un analyste maritime souhaitant étudier une flotte de navires ou bien un agent portuaire consultant l'historique des passages dans son port ou encore un gestionnaire de flotte suivant les navires sous sa responsabilité. Dans le cadre de ce projet, une partie des données provient de sources réelles et a été nettoyée, tandis que d'autres ont été générées de façon fictive mais réaliste afin d'obtenir une base suffisamment complète pour produire des requêtes intéressantes.


## Diagramme de classe UML
![Diagramme de classes UML du projet ShipData](images/SHIPDATA_UML.drawio.png)

*Figure 1: Diagramme de classes UML 
Nous l'avons fait sur draw.io et il présente les principales entités de la base de données ainsi que leurs relations : navires, types de navires, pavillons, sociétés de classification, constructeurs, propriétaires, ports et escales. La classe d’association ProprieteNavire permet de représenter l’historique des propriétaires d’un navire dans le temps*

## Définition des attributs

Évidemment, pas tout le monde connait le monde maritime donc les tableaux suivants présentent les attributs de chaque table de la base ShipData. Pour chaque attribut, il y a son nom, sa signification et son domaine de valeurs. Le domaine précise le type de donnée attendu ainsi que certaines contraintes importantes, comme les valeurs positives, les formats de date ou les références vers d’autres tables


### categorie_principale

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| id_categorie | Integer | PK, NOT NULL | Identifiant unique de la catégorie principale |
| nom_categorie | VARCHAR(100) | NOT NULL, UNIQUE | Nom de la catégorie générale du navire (ex. Cargo sec, Passager) |
| description | VARCHAR(500) | NOT NULL | Description textuelle |

---

### type_navire

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| id_type_navire | Integer | PK, NOT NULL | Identifiant unique du type de navire |
| nom_type | VARCHAR(150) | NOT NULL, UNIQUE | Nom précis du type de navire (ex. Container ship, Bulk carrier) |
| id_categorie | Integer | NOT NULL, FK -> categorie_principale | Catégorie principale à laquelle appartient le type |
| description | VARCHAR(500) | NOT NULL | Description du type de navire |

---

### pavillon

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| id_pavillon | Integer | PK, NOT NULL | Identifiant unique du pavillon |
| nom_pays | VARCHAR(100) | NOT NULL, UNIQUE | Nom du pays d'immatriculation |
| code_iso2 | CHAR(2) | UNIQUE (partiel) | Code ISO 3166-1 alpha-2 du pays + NULL admis (car Namibie = NA) |
| code_iso3 | CHAR(3) | NOT NULL, UNIQUE | Code ISO 3166-1 alpha-3 du pays |

---

### societe_classification

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| id_societe_classification | Integer | PK, NOT NULL | Identifiant unique de la société de classification |
| nom_societe | VARCHAR(150) | NOT NULL, UNIQUE | Nom complet de la société (ex. Bureau Veritas) |
| sigle | VARCHAR(20) | NOT NULL, UNIQUE | Sigle officiel de la société (ex. BV, DNV, LR) |
| code_iso2_pays | CHAR(2) | NOT NULL | Code ISO du pays de la société |
| site_web | VARCHAR(500) |  / | URL du site officiel de la société |

---

### port

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| id_port | Integer | PK, NOT NULL | Identifiant unique du port |
| nom_port | VARCHAR(150) | NOT NULL | Nom courant du port (ex. Savona) |
| nom_formel | VARCHAR(200) | NOT NULL, UNIQUE | Nom officiel complet du port (ex. Port of Beirut) |
| code_iso2_pays | CHAR(2) | NOT NULL | Code ISO du pays où se situe le port |
| latitude | NUMERIC(9,6) | NOT NULL | Latitude géographique du port (entre -90 et 90) |
| longitude | NUMERIC(9,6) | NOT NULL | Longitude géographique du port (entre -180 et 180) |
| taille_port | VARCHAR(50) | NOT NULL, CHECK | Taille du port : Very Small, Small, Medium ou Large |
| type_port | VARCHAR(100) | NOT NULL, CHECK | Type d'infrastructure portuaire (8 valeurs possibles) |
| capacite_max_navire | VARCHAR(50) | CHECK | Capacité maximale d'accueil : Under 500' ou Over 500' |

---

### constructeur

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| id_constructeur | Integer | PK, NOT NULL | Identifiant unique du chantier naval |
| nom_constructeur | VARCHAR(150) | NOT NULL, UNIQUE | Nom du chantier naval constructeur |
| code_iso2_pays | CHAR(2) | NOT NULL | Code ISO du pays où se situe le chantier |
| annee_fondation | Integer | NOT NULL, CHECK (1700–2030) | Année de fondation du chantier naval |
| ville_chantier | VARCHAR(100) | NOT NULL | Ville où est établi le chantier naval |

---

### proprietaire

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| id_proprietaire | Integer | PK, NOT NULL | Identifiant unique du propriétaire |
| nom_proprietaire | VARCHAR(150) | NOT NULL, UNIQUE | Nom de l'entreprise ou organisation propriétaire |
| code_iso2_pays | CHAR(2) | NOT NULL | Code ISO du pays du propriétaire |
| annee_creation | Integer | NOT NULL, CHECK (1700–2030) | Année de création de l'organisation propriétaire |
| ville_siege | VARCHAR(100) | NOT NULL | Ville du siège social |

---

### navire

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| imo | Integer | PK, NOT NULL, CHECK (7 chiffres) | IMO = identifiant maritime international|
| mmsi | Integer | NOT NULL, UNIQUE, CHECK (9 chiffres) | MMSI = identifiant radio du navire |
| nom_navire | VARCHAR(150) | NOT NULL | Nom commercial du navire |
| id_type_navire | Integer | NOT NULL, FK -> type_navire | Type de navire |
| id_pavillon | Integer | NOT NULL, FK -> pavillon | Pavillon d'immatriculation du navire |
| annee_construction | Integer | NOT NULL, CHECK (1900–2030) | Année de mise en service du navire |
| gross_tonnage | Integer | NOT NULL, CHECK > 0 | Tonnage brut = mesure du volume total du navire (en tonneaux) |
| deadweight_tonnage | Integer | NOT NULL, CHECK ≥ 0 | Port en lourd = charge maximale transportable (en T) |
| longueur_m | NUMERIC(6,2) | NOT NULL, CHECK > 0 | Longueur hors-tout du navire en mètres |
| largeur_m | NUMERIC(6,2) | NOT NULL, CHECK > 0 | Largeur maximale du navire en mètres |
| tirant_eau_m | NUMERIC(5,2) | NOT NULL, CHECK > 0 | Tirant d'eau maximal du navire en mètres |
| id_societe_classification | Integer | NOT NULL, FK -> societe_classification | Société de classification certifiant le navire |
| id_constructeur | Integer | NOT NULL, FK -> constructeur | Chantier naval ayant construit le navire |

---

### propriete_navire

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| imo | Integer | PK, NOT NULL, FK -> navire | Référence au navire concerné |
| id_proprietaire | Integer | PK, NOT NULL, FK -> proprietaire | Référence au propriétaire |
| date_debut | Date | PK, NOT NULL | Date de début de la période de propriété |
| date_fin | Date | CHECK (date_fin > date_debut) | Date de fin de la période de propriété & NULL si propriétaire actuel |

---

### escale

| Attribut | Domaine | Contraintes | Définition |
|---|---|---|---|
| id_escale | Integer | PK, NOT NULL | Identifiant unique de l'escale |
| imo | Integer | NOT NULL, FK -> navire | Référence au navire ayant effectué l'escale |
| id_port | Integer | NOT NULL, FK -> port | Référence au port visité |
| date_arrivee | Date | NOT NULL | Date d'arrivée du navire dans le port. Format YYYY-MM-DD|
| heure_arrivee | Time | / | Heure d'arrivée du navire dans le port. Format HH:MM:SS|
| date_depart | Date | CHECK (date_depart ≥ date_arrivee) | Date de départ du navire & NULL si escale en cours. Format YYYY-MM-DD|
| heure_depart | Time | / | Heure de départ du navire du port. Format HH:MM:SS|

--- 

## Justification de la troisième forme normale

Pour qu'une relation soit en 3FN, elle doit respecter trois conditions. En 1FN, chaque attribut contient une valeur unique et atomique. En 2FN, chaque attribut non-clé dépend de la totalité de la clé primaire et pas seulement d'une partie, ce qui concerne surtout les tables avec une clé composite. En 3FN, aucun attribut non-clé ne dépend d'un autre attribut non-clé : tout doit remonter directement à la clé.

Dans ShipData, on a séparé chaque concept dans sa propre table dès le départ. Cette séparation est justement ce qui nous permet de garantir l'absence de redondances et de dépendances indésirables.

categorie_principale: La clé primaire est id_categorie. Les attributs nom_categorie et description décrivent chacun directement la catégorie. La description ne dépend pas du nom de la catégorie : les deux sont des propriétés indépendantes de la catégorie elle-même. Aucune dépendance transitive n'est présente. La table est en 3FN.

type_navire: La clé primaire est id_type_navire. Les attributs nom_type et description décrivent directement le type de navire. L'attribut id_categorie est une clé étrangère qui relie le type à sa catégorie principale, mais les informations de cette catégorie restent dans la table categorie_principale et ne sont pas répétées ici. Pas de dépendance transitive. La table est en 3FN.

pavillon: La clé primaire est id_pavillon. Les attributs nom_pays, code_iso2 et code_iso3 décrivent directement le pays d'immatriculation. On aurait pu stocker ces informations dans la table navire, mais cela aurait répété le nom et les codes du pays pour chaque navire ayant le même pavillon. En isolant le pavillon dans sa propre table, on évite cette redondance. La table est en 3FN.

societe_classification: La clé primaire est id_societe_classification. Les attributs nom_societe, sigle, code_iso2_pays et site_web décrivent tous directement la société. Aucun ne dépend d'un autre : le sigle ne détermine pas le site web, et le pays ne détermine pas le nom. Tout remonte à la clé. La table est en 3FN.

port: La clé primaire est id_port. Tous les attributs, le nom, le nom formel, le pays, les coordonnées, la taille, le type et la capacité, décrivent directement le port. On aurait pu stocker certaines de ces informations dans la table escale, mais cela aurait dupliqué les données du port à chaque passage d'un navire. La séparation évite cette redondance. La table est en 3FN.

constructeur: La clé primaire est id_constructeur. Les attributs nom_constructeur, code_iso2_pays, annee_fondation et ville_chantier décrivent directement le chantier naval. Aucun ne dépend d'un autre : la ville ne détermine pas le pays, et l'année de fondation ne dépend pas du nom. La table est en 3FN.

proprietaire: La clé primaire est id_proprietaire. Les attributs nom_proprietaire, code_iso2_pays, annee_creation et ville_siege décrivent directement l'organisation propriétaire. La relation de propriété dans le temps est gérée séparément dans propriete_navire, ce qui évite de répéter les informations du propriétaire pour chaque navire qu'il possède ou a possédé. La table est en 3FN.

navire: La clé primaire est imo. Tous les attributs techniques comme mmsi, nom_navire, annee_construction, les tonnages et les dimensions décrivent directement le navire identifié par son numéro IMO. Les références vers le type, le pavillon, la société de classification et le constructeur sont représentées par des clés étrangères : les détails de ces entités restent dans leurs propres tables et ne sont jamais répétés dans navire. Pas de dépendance transitive. La table est en 3FN.

propriete_navire: La clé primaire est composite : (imo, id_proprietaire, date_debut). Le seul attribut non-clé est date_fin. Il dépend bien des trois composantes de la clé ensemble : il ne dépend pas de imo seul car un même navire peut avoir plusieurs propriétaires, ni de id_proprietaire seul car un même propriétaire peut détenir plusieurs navires à des périodes différentes, ni de date_debut seul. La 2FN est respectée. Et comme il n'y a qu'un seul attribut non-clé, aucune dépendance transitive n'est possible. La table est en 3FN.

escale: La clé primaire est id_escale. Les attributs imo et id_port sont des clés étrangères qui relient l'escale à un navire et à un port. Les attributs date_arrivee, heure_arrivee, date_depart et heure_depart décrivent directement l'événement et dépendent de l'escale elle-même, pas du navire ou du port. Les informations du navire et du port restent dans leurs tables respectives. La table est en 3FN.


### Conclusion

Donc, toutes les relations de ShipData respectent la 3FN. Le schéma a été pensé pour que chaque table représente un seul concept, que les attributs non-clés dépendent directement de la clé primaire, et que les informations liées à d'autres entités soient isolées dans leurs propres tables et référencées par clés étrangères. Cette structure limite les redondances, simplifie les mises à jour et garantit la cohérence de la base.
