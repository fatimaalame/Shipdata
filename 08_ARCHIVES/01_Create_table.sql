CREATE TABLE types_navires (
    id_type_navire INTEGER PRIMARY KEY,
    type_navire VARCHAR(150) NOT NULL,
    categorie_principale VARCHAR(200),
    description TEXT
);

CREATE TABLE pavillons (
    id_pavillon INTEGER PRIMARY KEY,
    code_pays VARCHAR(10),
    nom_pays VARCHAR(100) NOT NULL,
    code_iso2 CHAR(2),
    code_iso3 CHAR(3)
);

CREATE TABLE societes_classification (
    id_societe_classification INTEGER PRIMARY KEY,
    nom_societe VARCHAR(200) NOT NULL,
    sigle VARCHAR(30),
    pays_siege VARCHAR(100),
    site_web TEXT
);

CREATE TABLE constructeurs (
    id_constructeur INTEGER PRIMARY KEY,
    nom_constructeur VARCHAR(200) NOT NULL,
    pays VARCHAR(100),
    ville VARCHAR(100),
    annee_fondation INTEGER,
    type_activite VARCHAR(150)
);

CREATE TABLE proprietaires (
    id_proprietaire INTEGER PRIMARY KEY,
    nom_proprietaire VARCHAR(200) NOT NULL,
    type_organisation VARCHAR(100),
    pays VARCHAR(100),
    adresse TEXT,
    site_web TEXT
);


CREATE TABLE port_data (
    formal_name VARCHAR(200),
    index_no INTEGER UNIQUE,
    region INTEGER,
    country_code VARCHAR(10),
    country VARCHAR(100),
    port VARCHAR(150) NOT NULL,
    degrees_lat INTEGER,
    minutes_lat INTEGER,
    direction_lat CHAR(1),
    degrees_long INTEGER,
    minutes_long INTEGER,
    direction_long CHAR(1),
    coordinates VARCHAR(100),
    sailing_directions_publication VARCHAR(100),
    charts VARCHAR(100),
    harbor_size VARCHAR(100),
    harbor_type VARCHAR(150),
    shelter_afforded VARCHAR(100),
    entrance_restrictions_tide VARCHAR(20),
    entrance_restrictions_swell VARCHAR(20),
    entrance_restrictions_ice VARCHAR(20),
    entrance_restrictions_other VARCHAR(20),
    overhead_limits VARCHAR(20),
    channel_depth VARCHAR(100),
    anchorage_depth VARCHAR(100),
    cargo_pier_depth VARCHAR(100),
    oil_lng_terminal_depth VARCHAR(100),
    tide INTEGER,
    max_size_vessel VARCHAR(100),
    good_holding_ground VARCHAR(20),
    turning_area VARCHAR(20),
    first_port_of_entry VARCHAR(20),
    us_representative VARCHAR(20),
    eta_message VARCHAR(20),
    compulsory_pilotage VARCHAR(20),
    available_pilotage VARCHAR(20),
    local_assist_pilotage VARCHAR(20),
    pilotage_advisable VARCHAR(20),
    tug_salvage VARCHAR(20),
    tug_assist VARCHAR(20),
    quarantine_pratique VARCHAR(20),
    quarantine_sscc_cert VARCHAR(20),
    quarantine_other VARCHAR(20),
    com_telephone VARCHAR(20),
    com_telefax VARCHAR(20),
    com_radio VARCHAR(20),
    com_radio_tel VARCHAR(20),
    com_air VARCHAR(20),
    com_rail VARCHAR(20),
    load_offload_wharves VARCHAR(20),
    load_offload_anchor VARCHAR(20),
    load_offload_med_moor VARCHAR(20),
    load_offload_beach_moor VARCHAR(20),
    load_offload_ice_moor VARCHAR(20),
    medical_facilities VARCHAR(20),
    garbage_disposal VARCHAR(20),
    degauss VARCHAR(20),
    dirty_ballast VARCHAR(20),
    fixed_cranes VARCHAR(20),
    mobile_cranes VARCHAR(20),
    floating_cranes VARCHAR(20),
    lifts_100_tons_plus VARCHAR(20),
    lifts_50_100_tons VARCHAR(20),
    lifts_25_49_tons VARCHAR(20),
    lifts_0_24_tons VARCHAR(20),
    longshore_services VARCHAR(20),
    electrical_services VARCHAR(20),
    steam_services VARCHAR(20),
    navigation_equipment_services VARCHAR(20),
    electrical_repair_services VARCHAR(20),
    supplies_provisions VARCHAR(20),
    supplies_water VARCHAR(20),
    supplies_fuel_oil VARCHAR(20),
    supplies_diesel_oil VARCHAR(20),
    supplies_deck VARCHAR(20),
    supplies_engine VARCHAR(20),
    repair VARCHAR(100),
    drydock VARCHAR(100),
    railway VARCHAR(100)
);

CREATE TABLE navire (
    imo INTEGER PRIMARY KEY,
    mmsi BIGINT UNIQUE,
    nom_navire VARCHAR(200) NOT NULL,
    id_type_navire INTEGER,
    drapeau VARCHAR(100),
    annee_construction INTEGER,
    gross_tonnage INTEGER,
    deadweight_tonnage INTEGER,
    longueur_m NUMERIC(8,2),
    largeur_m NUMERIC(8,2),
    tirant_eau_m NUMERIC(8,2),
    capacite_teu INTEGER,
    id_pavillon INTEGER,
    id_societe_classification INTEGER,
    id_constructeur INTEGER,
    id_proprietaire_actuel INTEGER
);


CREATE TABLE escales (
    id_escale INTEGER PRIMARY KEY,
    imo INTEGER,
    index_no INTEGER,
    nom_port VARCHAR(150),
    pays_port VARCHAR(100),
    date_arrivee DATE,
    heure_arrivee TIME,
    date_depart DATE,
    heure_depart TIME,
    statut_escale VARCHAR(100),
    capacite_port_disponible INTEGER
);

