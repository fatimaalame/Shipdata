ALTER TABLE categorie_principale ADD CONSTRAINT pk_categorie_principale PRIMARY KEY (id_categorie);
ALTER TABLE type_navire ADD CONSTRAINT pk_type_navire PRIMARY KEY (id_type_navire);
ALTER TABLE pavillon ADD CONSTRAINT pk_pavillon PRIMARY KEY (id_pavillon);
ALTER TABLE societe_classification ADD CONSTRAINT pk_societe_classification PRIMARY KEY (id_societe_classification);
ALTER TABLE port ADD CONSTRAINT pk_port PRIMARY KEY (id_port);
ALTER TABLE constructeur ADD CONSTRAINT pk_constructeur PRIMARY KEY (id_constructeur);
ALTER TABLE proprietaire ADD CONSTRAINT pk_proprietaire PRIMARY KEY (id_proprietaire);
ALTER TABLE navire ADD CONSTRAINT pk_navire PRIMARY KEY (imo);
ALTER TABLE escale ADD CONSTRAINT pk_escale PRIMARY KEY (id_escale);

ALTER TABLE propriete_navire ADD CONSTRAINT pk_propriete_navire PRIMARY KEY (imo, id_proprietaire, date_debut);


ALTER TABLE pavillon ADD CONSTRAINT uk_pavillon_code_iso2 UNIQUE (code_iso2);


ALTER TABLE type_navire ADD CONSTRAINT fk_type_navire_categorie FOREIGN KEY (id_categorie) REFERENCES categorie_principale(id_categorie);


ALTER TABLE port ADD CONSTRAINT fk_port_pavillon FOREIGN KEY (code_iso2_pays) REFERENCES pavillon(code_iso2);
ALTER TABLE constructeur ADD CONSTRAINT fk_constructeur_pavillon FOREIGN KEY (code_iso2_pays) REFERENCES pavillon(code_iso2);
ALTER TABLE proprietaire ADD CONSTRAINT fk_proprietaire_pavillon FOREIGN KEY (code_iso2_pays) REFERENCES pavillon(code_iso2);
ALTER TABLE societe_classification ADD CONSTRAINT fk_societe_classification_pavillon FOREIGN KEY (code_iso2_pays) REFERENCES pavillon(code_iso2);


ALTER TABLE navire ADD CONSTRAINT fk_navire_type FOREIGN KEY (id_type_navire) REFERENCES type_navire(id_type_navire);
ALTER TABLE navire ADD CONSTRAINT fk_navire_pavillon FOREIGN KEY (id_pavillon) REFERENCES pavillon(id_pavillon);
ALTER TABLE navire ADD CONSTRAINT fk_navire_classification FOREIGN KEY (id_societe_classification) REFERENCES societe_classification(id_societe_classification);
ALTER TABLE navire ADD CONSTRAINT fk_navire_constructeur FOREIGN KEY (id_constructeur) REFERENCES constructeur(id_constructeur);


ALTER TABLE propriete_navire ADD CONSTRAINT fk_propriete_navire FOREIGN KEY (imo) REFERENCES navire(imo);
ALTER TABLE propriete_navire ADD CONSTRAINT fk_propriete_proprietaire FOREIGN KEY (id_proprietaire) REFERENCES proprietaire(id_proprietaire);


ALTER TABLE escale ADD CONSTRAINT fk_escale_navire FOREIGN KEY (imo) REFERENCES navire(imo);
ALTER TABLE escale ADD CONSTRAINT fk_escale_port FOREIGN KEY (id_port) REFERENCES port(id_port);

ALTER TABLE navire ADD CONSTRAINT uk_navire_mmsi UNIQUE (mmsi);


ALTER TABLE categorie_principale ADD CONSTRAINT uk_categorie_principale_nom UNIQUE (nom_categorie);
ALTER TABLE type_navire ADD CONSTRAINT uk_type_navire_nom UNIQUE (nom_type);
ALTER TABLE pavillon ADD CONSTRAINT uk_pavillon_nom_pays UNIQUE (nom_pays);
ALTER TABLE pavillon ADD CONSTRAINT uk_pavillon_code_iso3 UNIQUE (code_iso3);
ALTER TABLE societe_classification ADD CONSTRAINT uk_societe_classification_nom UNIQUE (nom_societe);
ALTER TABLE societe_classification ADD CONSTRAINT uk_societe_classification_sigle UNIQUE (sigle);
ALTER TABLE constructeur ADD CONSTRAINT uk_constructeur_nom UNIQUE (nom_constructeur);
ALTER TABLE proprietaire ADD CONSTRAINT uk_proprietaire_nom UNIQUE (nom_proprietaire);


ALTER TABLE navire ADD CONSTRAINT ck_navire_annee CHECK (annee_construction >= 1900 AND annee_construction <= 2030);
ALTER TABLE navire ADD CONSTRAINT ck_navire_gt_positif CHECK (gross_tonnage > 0);
ALTER TABLE navire ADD CONSTRAINT ck_navire_dwt_positif CHECK (deadweight_tonnage > 0);
ALTER TABLE navire ADD CONSTRAINT ck_navire_dimensions_positives CHECK (longueur_m > 0 AND largeur_m > 0 AND tirant_eau_m > 0);


ALTER TABLE constructeur ADD CONSTRAINT ck_constructeur_annee CHECK (annee_fondation >= 1700 AND annee_fondation <= 2030);
ALTER TABLE proprietaire ADD CONSTRAINT ck_proprietaire_annee CHECK (annee_creation >= 1700 AND annee_creation <= 2030);


ALTER TABLE port ADD CONSTRAINT ck_port_latitude CHECK (latitude >= -90 AND latitude <= 90);
ALTER TABLE port ADD CONSTRAINT ck_port_longitude CHECK (longitude >= -180 AND longitude <= 180);
ALTER TABLE port ADD CONSTRAINT ck_port_taille CHECK (taille_port IN ('Very Small', 'Small', 'Medium', 'Large'));
ALTER TABLE port ADD CONSTRAINT ck_port_type CHECK (type_port IN ('Coastal Breakwater', 'Coastal Natural', 'Coastal Tide Gate', 'River Natural', 'River Basin', 'River Tide Gate', 'Lake or Canal', 'Open Roadstead'));
ALTER TABLE port ADD CONSTRAINT ck_port_capacite CHECK (capacite_max_navire IN ('Under 500''', 'Over 500'''));


ALTER TABLE propriete_navire ADD CONSTRAINT ck_propriete_dates CHECK (date_fin IS NULL OR date_fin > date_debut);
ALTER TABLE escale ADD CONSTRAINT ck_escale_dates CHECK (date_depart IS NULL OR date_depart > date_arrivee);


