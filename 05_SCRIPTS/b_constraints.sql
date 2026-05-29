-- PK

ALTER TABLE categorie_principale
    ADD CONSTRAINT pk_categorie_principale
    PRIMARY KEY (id_categorie);

ALTER TABLE type_navire
    ADD CONSTRAINT pk_type_navire
    PRIMARY KEY (id_type_navire);

ALTER TABLE pavillon
    ADD CONSTRAINT pk_pavillon
    PRIMARY KEY (id_pavillon);

ALTER TABLE societe_classification
    ADD CONSTRAINT pk_societe_classification
    PRIMARY KEY (id_societe_classification);

ALTER TABLE port
    ADD CONSTRAINT pk_port
    PRIMARY KEY (id_port);

ALTER TABLE constructeur
    ADD CONSTRAINT pk_constructeur
    PRIMARY KEY (id_constructeur);

ALTER TABLE proprietaire
    ADD CONSTRAINT pk_proprietaire
    PRIMARY KEY (id_proprietaire);

ALTER TABLE navire
    ADD CONSTRAINT pk_navire
    PRIMARY KEY (imo);

ALTER TABLE propriete_navire
    ADD CONSTRAINT pk_propriete_navire
    PRIMARY KEY (imo, id_proprietaire, date_debut);

ALTER TABLE escale
    ADD CONSTRAINT pk_escale
    PRIMARY KEY (id_escale);


-- FK

ALTER TABLE type_navire
    ADD CONSTRAINT fk_type_navire_categorie
    FOREIGN KEY (id_categorie)
    REFERENCES categorie_principale (id_categorie)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

ALTER TABLE navire
    ADD CONSTRAINT fk_navire_type_navire
    FOREIGN KEY (id_type_navire)
    REFERENCES type_navire (id_type_navire)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

ALTER TABLE navire
    ADD CONSTRAINT fk_navire_pavillon
    FOREIGN KEY (id_pavillon)
    REFERENCES pavillon (id_pavillon)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

ALTER TABLE navire
    ADD CONSTRAINT fk_navire_societe_classification
    FOREIGN KEY (id_societe_classification)
    REFERENCES societe_classification (id_societe_classification)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

ALTER TABLE navire
    ADD CONSTRAINT fk_navire_constructeur
    FOREIGN KEY (id_constructeur)
    REFERENCES constructeur (id_constructeur)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

ALTER TABLE propriete_navire
    ADD CONSTRAINT fk_propriete_navire_navire
    FOREIGN KEY (imo)
    REFERENCES navire (imo)
    ON UPDATE CASCADE
    ON DELETE CASCADE;

ALTER TABLE propriete_navire
    ADD CONSTRAINT fk_propriete_navire_proprietaire
    FOREIGN KEY (id_proprietaire)
    REFERENCES proprietaire (id_proprietaire)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;

ALTER TABLE escale
    ADD CONSTRAINT fk_escale_navire
    FOREIGN KEY (imo)
    REFERENCES navire (imo)
    ON UPDATE CASCADE
    ON DELETE CASCADE;

ALTER TABLE escale
    ADD CONSTRAINT fk_escale_port
    FOREIGN KEY (id_port)
    REFERENCES port (id_port)
    ON UPDATE CASCADE
    ON DELETE RESTRICT;


-- UNIQUE

ALTER TABLE categorie_principale
    ADD CONSTRAINT uk_categorie_principale_nom
    UNIQUE (nom_categorie);

ALTER TABLE type_navire
    ADD CONSTRAINT uk_type_navire_nom
    UNIQUE (nom_type);

ALTER TABLE pavillon
    ADD CONSTRAINT uk_pavillon_nom_pays
    UNIQUE (nom_pays);

ALTER TABLE pavillon
    ADD CONSTRAINT uk_pavillon_code_iso3
    UNIQUE (code_iso3);

CREATE UNIQUE INDEX uk_pavillon_code_iso2
    ON pavillon (code_iso2)
    WHERE code_iso2 IS NOT NULL;

ALTER TABLE societe_classification
    ADD CONSTRAINT uk_societe_classification_nom
    UNIQUE (nom_societe);

ALTER TABLE societe_classification
    ADD CONSTRAINT uk_societe_classification_sigle
    UNIQUE (sigle);

ALTER TABLE constructeur
    ADD CONSTRAINT uk_constructeur_nom
    UNIQUE (nom_constructeur);

ALTER TABLE proprietaire
    ADD CONSTRAINT uk_proprietaire_nom
    UNIQUE (nom_proprietaire);

ALTER TABLE navire
    ADD CONSTRAINT uk_navire_mmsi
    UNIQUE (mmsi);


-- CHECK

ALTER TABLE constructeur
    ADD CONSTRAINT ck_constructeur_annee_fondation
    CHECK (annee_fondation BETWEEN 1700 AND 2026);

ALTER TABLE proprietaire
    ADD CONSTRAINT ck_proprietaire_annee_creation
    CHECK (annee_creation BETWEEN 1700 AND 2026);

ALTER TABLE navire
    ADD CONSTRAINT ck_navire_annee_construction
    CHECK (annee_construction BETWEEN 1900 AND 2026);

ALTER TABLE navire
    ADD CONSTRAINT ck_navire_gross_tonnage
    CHECK (gross_tonnage > 0);

ALTER TABLE navire
    ADD CONSTRAINT ck_navire_deadweight_tonnage
    CHECK (deadweight_tonnage >= 0);

ALTER TABLE navire
    ADD CONSTRAINT ck_navire_longueur
    CHECK (longueur_m > 0);

ALTER TABLE navire
    ADD CONSTRAINT ck_navire_largeur
    CHECK (largeur_m > 0);

ALTER TABLE navire
    ADD CONSTRAINT ck_navire_tirant_eau
    CHECK (tirant_eau_m > 0);

ALTER TABLE port
    ADD CONSTRAINT ck_port_latitude
    CHECK (latitude BETWEEN -90 AND 90);

ALTER TABLE port
    ADD CONSTRAINT ck_port_longitude
    CHECK (longitude BETWEEN -180 AND 180);

ALTER TABLE port
    ADD CONSTRAINT ck_port_taille
    CHECK (taille_port IN ('Very Small', 'Small', 'Medium', 'Large'));

ALTER TABLE port
    ADD CONSTRAINT ck_port_type
    CHECK (
        type_port IN (
            'Coastal Breakwater',
            'Coastal Natural',
            'Coastal Tide Gate',
            'Lake or Canal',
            'Open Roadstead',
            'River Basin',
            'River Natural',
            'River Tide Gate'
        )
    );

ALTER TABLE port
    ADD CONSTRAINT ck_port_capacite_max
    CHECK (capacite_max_navire IN ('Over 500''', 'Under 500'''));

ALTER TABLE propriete_navire
    ADD CONSTRAINT ck_propriete_navire_dates
    CHECK (date_fin IS NULL OR date_fin > date_debut);

ALTER TABLE escale
    ADD CONSTRAINT ck_escale_dates
    CHECK (
        date_depart IS NULL
        OR date_depart > date_arrivee
        OR (
            date_depart = date_arrivee
            AND heure_depart IS NOT NULL
            AND heure_arrivee IS NOT NULL
            AND heure_depart > heure_arrivee
        )
    );