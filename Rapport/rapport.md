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

### `categorie_principale`

| Attribut | Signification | Domaine |
|---|---|---|
| `id_categorie` | Identifiant unique de la catégorie principale de navire | Entier positif |
| `nom_categorie` | Nom de la catégorie générale du navire | Texte court NON NULL |
| `description` | Description de la catégorie principale | Texte descriptif NON NULL |

### `type_navire`

| Attribut | Signification | Domaine |
|---|---|---|
| `id_type_navire` | Identifiant unique du type de navire | Entier positif |
| `nom_type` | Nom précis du type de navire | Texte court NON NULL |
| `id_categorie` | Catégorie principale à laquelle appartient le type de navire | Entier positif, clé étrangère vers `categorie_principale(id_categorie)` |
| `description` | Description du type de navire | Texte descriptif NON NULL |

### `pavillon`

| Attribut | Signification | Domaine |
|---|---|---|
| `id_pavillon` | Identifiant unique du pavillon | Entier positif |
| `nom_pays` | Nom du pays sous lequel un navire est immatriculé | Texte court NON NULL |
| `code_iso2` | Code ISO du pays sur deux lettres | Texte de 2 caractères, peut être NULL si l’information n’est pas disponible |
| `code_iso3` | Code ISO du pays sur trois lettres | Texte de 3 caractères NON NULL |

### `societe_classification`

| Attribut | Signification | Domaine |
|---|---|---|
| `id_societe_classification` | Identifiant unique de la société de classification | Entier positif |
| `nom_societe` | Nom complet de la société de classification maritime | Texte court NON NULL |
| `sigle` | Sigle de la société de classification | Texte court NON NULL, par exemple `DNV`, `ABS`, `LR` |
| `code_iso2_pays` | Code ISO du pays où se situe la société de classification | Texte de 2 caractères NON NULL |
| `site_web` | Site web officiel de la société de classification | Texte NON NULL correspondant à une URL |

### `port`

| Attribut | Signification | Domaine |
|---|---|---|
| `id_port` | Identifiant unique du port | Entier positif |
| `nom_port` | Nom court ou courant du port | Texte court NON NULL |
| `nom_formel` | Nom officiel ou complet du port | Texte NON NULL |
| `code_iso2_pays` | Code ISO du pays où se situe le port | Texte de 2 caractères NON NULL |
| `latitude` | Latitude géographique du port | Nombre décimal NON NULL entre -90 et 90 |
| `longitude` | Longitude géographique du port | Nombre décimal NON NULL entre -180 et 180 |
| `taille_port` | Taille du port | Texte NON NULL parmi `Very Small`, `Small`, `Medium`, `Large` |
| `type_port` | Type géographique ou technique du port | Texte NON NULL, par exemple `Coastal Natural`, `River Basin`, `Open Roadstead` |
| `capacite_max_navire` | Indication de la capacité maximale des navires pouvant accéder au port | Texte NON NULL, par exemple `Over 500'` ou `Under 500'` |

### `constructeur`

| Attribut | Signification | Domaine |
|---|---|---|
| `id_constructeur` | Identifiant unique du constructeur naval | Entier positif |
| `nom_constructeur` | Nom du chantier naval ou du groupe constructeur | Texte court NON NULL |
| `code_iso2_pays` | Code ISO du pays du constructeur | Texte de 2 caractères NON NULL |
| `annee_fondation` | Année de fondation du constructeur | Entier NON NULL compris entre 1700 et 2026 |
| `ville_chantier` | Ville principale associée au chantier naval | Texte court NON NULL |

### `proprietaire`

| Attribut | Signification | Domaine |
|---|---|---|
| `id_proprietaire` | Identifiant unique du propriétaire | Entier positif |
| `nom_proprietaire` | Nom de l’entreprise ou organisation propriétaire | Texte court NON NULL |
| `code_iso2_pays` | Code ISO du pays du propriétaire | Texte de 2 caractères NON NULL |
| `annee_creation` | Année de création de l’organisation propriétaire | Entier NON NULL compris entre 1700 et 2026 |
| `ville_siege` | Ville du siège ou de référence du propriétaire | Texte court NON NULL |

### `navire`

| Attribut | Signification | Domaine |
|---|---|---|
| `imo` | Numéro IMO du navire, utilisé comme identifiant unique dans la base | Entier positif, clé primaire |
| `mmsi` | Numéro MMSI du navire, utilisé dans les systèmes d’identification maritime | Entier positif NON NULL, valeur unique |
| `nom_navire` | Nom du navire | Texte court NON NULL |
| `id_type_navire` | Type auquel appartient le navire | Entier positif, clé étrangère vers `type_navire(id_type_navire)` |
| `id_pavillon` | Pavillon sous lequel le navire est immatriculé | Entier positif, clé étrangère vers `pavillon(id_pavillon)` |
| `annee_construction` | Année de construction du navire | Entier NON NULL compris entre 1900 et 2026 |
| `gross_tonnage` | Jauge brute du navire | Entier strictement positif |
| `deadweight_tonnage` | Port en lourd du navire, c’est-à-dire sa capacité de charge | Entier positif ou nul |
| `longueur_m` | Longueur du navire en mètres | Nombre décimal strictement positif |
| `largeur_m` | Largeur du navire en mètres | Nombre décimal strictement positif |
| `tirant_eau_m` | Tirant d’eau du navire en mètres | Nombre décimal strictement positif |
| `id_societe_classification` | Société de classification associée au navire | Entier positif, clé étrangère vers `societe_classification(id_societe_classification)` |
| `id_constructeur` | Constructeur du navire | Entier positif, clé étrangère vers `constructeur(id_constructeur)` |

### `propriete_navire`

| Attribut | Signification | Domaine |
|---|---|---|
| `imo` | Navire concerné par la période de propriété | Entier positif, clé étrangère vers `navire(imo)` |
| `id_proprietaire` | Propriétaire concerné par la période de propriété | Entier positif, clé étrangère vers `proprietaire(id_proprietaire)` |
| `date_debut` | Date de début de la période pendant laquelle le propriétaire possède le navire | Date NON NULL au format `YYYY-MM-DD` |
| `date_fin` | Date de fin de la période de propriété, une valeur NULL indique que le propriétaire est actuel | Date au format `YYYY-MM-DD`, peut être `NULL` |

### `escale`

| Attribut | Signification | Domaine |
|---|---|---|
| `id_escale` | Identifiant unique de l’escale | Entier positif |
| `imo` | Navire ayant effectué l’escale | Entier positif, clé étrangère vers `navire(imo)` |
| `id_port` | Port dans lequel l’escale a lieu | Entier positif, clé étrangère vers `port(id_port)` |
| `date_arrivee` | Date d’arrivée du navire au port | Date NON NULL au format `YYYY-MM-DD` |
| `heure_arrivee` | Heure d’arrivée du navire au port | Heure au format `HH:MM:SS`, peut être NULL |
| `date_depart` | Date de départ du navire du port | Date au format `YYYY-MM-DD`, peut être NULL |
| `heure_depart` | Heure de départ du navire du port | Heure au format `HH:MM:SS`, peut être NULL |