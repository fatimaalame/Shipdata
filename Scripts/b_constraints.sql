CREATE TABLE categorie_principale (
    id_categorie INTEGER NOT NULL,
    nom_categorie VARCHAR(100) NOT NULL,
    description VARCHAR(500) NOT NULL
);


CREATE TABLE type_navire (
    id_type_navire INTEGER NOT NULL,
    nom_type VARCHAR(150) NOT NULL,
    id_categorie INTEGER NOT NULL,
    description VARCHAR(500) NOT NULL
);

CREATE TABLE pavillon (
    id_pavillon INTEGER NOT NULL,
    nom_pays VARCHAR(100) NOT NULL,
    code_iso2 CHAR(2),
    code_iso3 CHAR(3) NOT NULL
);

CREATE TABLE societe_classification (
    id_societe_classification INTEGER NOT NULL,
    nom_societe VARCHAR(150) NOT NULL,
    sigle VARCHAR(20) NOT NULL,
    code_iso2_pays CHAR(2) NOT NULL,
    site_web VARCHAR(500) NOT NULL
);

CREATE TABLE port (
    id_port INTEGER NOT NULL,
    nom_port VARCHAR(150) NOT NULL,
    nom_formel VARCHAR(200) NOT NULL,
    code_iso2_pays CHAR(2) NOT NULL,
    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL,
    taille_port VARCHAR(50) NOT NULL,
    type_port VARCHAR(100) NOT NULL,
    capacite_max_navire VARCHAR(50) NOT NULL
);

CREATE TABLE constructeur (
    id_constructeur INTEGER NOT NULL,
    nom_constructeur VARCHAR(150) NOT NULL,
    code_iso2_pays CHAR(2) NOT NULL,
    annee_fondation INTEGER NOT NULL,
    ville_chantier VARCHAR(100) NOT NULL
);

CREATE TABLE proprietaire (
    id_proprietaire INTEGER NOT NULL,
    nom_proprietaire VARCHAR(150) NOT NULL,
    code_iso2_pays CHAR(2) NOT NULL,
    annee_creation INTEGER NOT NULL,
    ville_siege VARCHAR(100) NOT NULL
);

CREATE TABLE navire (
    imo INTEGER NOT NULL,
    mmsi INTEGER NOT NULL,
    nom_navire VARCHAR(150) NOT NULL,
    id_type_navire INTEGER NOT NULL,
    id_pavillon INTEGER NOT NULL,
    annee_construction INTEGER NOT NULL,
    gross_tonnage INTEGER NOT NULL,
    deadweight_tonnage INTEGER NOT NULL,
    longueur_m NUMERIC(6,2) NOT NULL,
    largeur_m NUMERIC(6,2) NOT NULL,
    tirant_eau_m NUMERIC(5,2) NOT NULL,
    id_societe_classification INTEGER NOT NULL,
    id_constructeur INTEGER NOT NULL
);

CREATE TABLE propriete_navire (
    imo INTEGER NOT NULL,
    id_proprietaire INTEGER NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE
);

CREATE TABLE escale (
    id_escale INTEGER NOT NULL,
    imo INTEGER NOT NULL,
    id_port INTEGER NOT NULL,
    date_arrivee DATE NOT NULL,
    heure_arrivee TIME,
    date_depart DATE,
    heure_depart TIME   
);
