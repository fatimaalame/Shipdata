ALTER TABLE navire
ADD CONSTRAINT fk_navire_type
FOREIGN KEY (id_type_navire)
REFERENCES types_navires(id_type_navire);

ALTER TABLE navire
ADD CONSTRAINT fk_navire_pavillon
FOREIGN KEY (id_pavillon)
REFERENCES pavillons(id_pavillon);

ALTER TABLE navire
ADD CONSTRAINT fk_navire_societe_classification
FOREIGN KEY (id_societe_classification)
REFERENCES societes_classification(id_societe_classification);

ALTER TABLE navire
ADD CONSTRAINT fk_navire_constructeur
FOREIGN KEY (id_constructeur)
REFERENCES constructeurs(id_constructeur);

ALTER TABLE navire
ADD CONSTRAINT fk_navire_proprietaire
FOREIGN KEY (id_proprietaire_actuel)
REFERENCES proprietaires(id_proprietaire);

ALTER TABLE escales
ADD CONSTRAINT fk_escales_navire
FOREIGN KEY (imo)
REFERENCES navire(imo);

ALTER TABLE escales
ADD CONSTRAINT fk_escales_port
FOREIGN KEY (index_no)
REFERENCES port_data(index_no);