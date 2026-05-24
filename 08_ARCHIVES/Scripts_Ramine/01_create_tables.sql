CREATE TABLE categorie_principale (
    id_categorie INTEGER,
    nom_categorie VARCHAR(50) NOT NULL,
    description VARCHAR(200) NOT NULL
);

CREATE TABLE pavillon (
    id_pavillon INTEGER,
    nom_pays VARCHAR(80) NOT NULL,
    code_iso2 CHAR(2) NOT NULL,
    code_iso3 CHAR(3) NOT NULL
);

CREATE TABLE type_navire (
    id_type_navire INTEGER,
    nom_type VARCHAR(80) NOT NULL,
    id_categorie INTEGER NOT NULL,
    description VARCHAR(200) NOT NULL
);

CREATE TABLE societe_classification (
    id_societe_classification INTEGER,
    nom_societe VARCHAR(120) NOT NULL,
    sigle VARCHAR(10) NOT NULL,
    code_iso2_pays CHAR(2) NOT NULL
);

CREATE TABLE port (
    id_port INTEGER,
    nom_port VARCHAR(100) NOT NULL,
    nom_formel VARCHAR(150) NOT NULL,
    code_iso2_pays CHAR(2) NOT NULL,
    latitude NUMERIC(8,5) NOT NULL,
    longitude NUMERIC(8,5) NOT NULL,
    taille_port VARCHAR(10) NOT NULL,
    type_port VARCHAR(30) NOT NULL,
    capacite_max_navire VARCHAR(10) NOT NULL
);

CREATE TABLE constructeur (
    id_constructeur INTEGER,
    nom_constructeur VARCHAR(120) NOT NULL,
    code_iso2_pays CHAR(2) NOT NULL,
    annee_fondation SMALLINT NOT NULL,
    ville_chantier VARCHAR(80) NOT NULL
);

CREATE TABLE navire (
    imo INTEGER,
    mmsi INTEGER NOT NULL,
    nom_navire VARCHAR(100) NOT NULL,
    id_type_navire INTEGER NOT NULL,
    id_pavillon INTEGER NOT NULL,
    annee_construction SMALLINT NOT NULL,
    gross_tonnage INTEGER NOT NULL,
    deadweight_tonnage INTEGER NOT NULL,
    longueur_m NUMERIC(6,2) NOT NULL,
    largeur_m NUMERIC(5,2) NOT NULL,
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
    id_escale INTEGER,
    imo INTEGER NOT NULL,
    id_port INTEGER NOT NULL,
    date_arrivee TIMESTAMP NOT NULL,
    date_depart TIMESTAMP
);