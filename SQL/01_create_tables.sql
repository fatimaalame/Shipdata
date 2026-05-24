DROP TABLE IF EXISTS escale;
DROP TABLE IF EXISTS propriete_navire;
DROP TABLE IF EXISTS navire;
DROP TABLE IF EXISTS proprietaire;
DROP TABLE IF EXISTS constructeur;
DROP TABLE IF EXISTS port;
DROP TABLE IF EXISTS societe_classification;
DROP TABLE IF EXISTS pavillon;
DROP TABLE IF EXISTS type_navire;
DROP TABLE IF EXISTS categorie_principale;

CREATE TABLE categorie_principale (
    id_categorie INTEGER NOT NULL,
    nom_categorie VARCHAR(100) NOT NULL,
    description VARCHAR(500)
);

CREATE TABLE type_navire (
    id_type_navire INTEGER NOT NULL,
    nom_type VARCHAR(150) NOT NULL,
    id_categorie INTEGER NOT NULL,
    description VARCHAR(500)
);

CREATE TABLE pavillon (
    id_pavillon INTEGER NOT NULL,
    nom_pays VARCHAR(100) NOT NULL,
    code_iso2 CHAR(2) NOT NULL,
    code_iso3 CHAR(3) NOT NULL
);

CREATE TABLE societe_classification (
    id_societe_classification INTEGER NOT NULL,
    nom_societe VARCHAR(150) NOT NULL,
    sigle VARCHAR(20) NOT NULL,
    code_iso2_pays CHAR(2),
    site_web VARCHAR(500)
);

CREATE TABLE port (
    id_port INTEGER NOT NULL,
    nom_port VARCHAR(150) NOT NULL,
    pays VARCHAR(100),
    ville VARCHAR(100),
    region VARCHAR(100),
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    harbor_size VARCHAR(50),
    harbor_type VARCHAR(100)
);

CREATE TABLE constructeur (
    id_constructeur INTEGER NOT NULL,
    nom_constructeur VARCHAR(150) NOT NULL,
    pays VARCHAR(100),
    ville VARCHAR(100),
    annee_fondation INTEGER
);

CREATE TABLE proprietaire (
    id_proprietaire INTEGER NOT NULL,
    nom_proprietaire VARCHAR(150) NOT NULL,
    type_organisation VARCHAR(100),
    pays VARCHAR(100),
    ville VARCHAR(100)
);

CREATE TABLE navire (
    imo INTEGER NOT NULL,
    mmsi INTEGER,
    nom_navire VARCHAR(150) NOT NULL,
    id_type_navire INTEGER NOT NULL,
    id_pavillon INTEGER NOT NULL,
    annee_construction INTEGER,
    gross_tonnage INTEGER,
    deadweight_tonnage INTEGER,
    longueur_m NUMERIC(6,2),
    largeur_m NUMERIC(6,2),
    tirant_eau_m NUMERIC(5,2),
    capacite_teu INTEGER,
    id_societe_classification INTEGER,
    id_constructeur INTEGER
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