CREATE VIEW v_navire_complet AS
SELECT n.imo,
       n.mmsi,
       n.nom_navire,
       tn.nom_type,
       p.nom_pays AS pavillon,
       n.annee_construction,
       n.gross_tonnage,
       n.deadweight_tonnage,
       n.longueur_m,
       n.largeur_m,
       n.tirant_eau_m,
       sc.sigle AS classification,
       c.nom_constructeur
FROM navire n
INNER JOIN type_navire tn ON n.id_type_navire = tn.id_type_navire
INNER JOIN pavillon p ON n.id_pavillon = p.id_pavillon
INNER JOIN societe_classification sc ON n.id_societe_classification = sc.id_societe_classification
INNER JOIN constructeur c ON n.id_constructeur = c.id_constructeur;

CREATE VIEW v_proprietaire_actuel AS
SELECT n.imo,
       n.nom_navire,
       pr.nom_proprietaire,
       pr.code_iso2_pays AS pays_proprietaire,
       pn.date_debut AS date_acquisition
FROM propriete_navire pn
INNER JOIN navire n ON pn.imo = n.imo
INNER JOIN proprietaire pr ON pn.id_proprietaire = pr.id_proprietaire
WHERE pn.date_fin IS NULL;

CREATE VIEW v_activite_port AS
SELECT po.id_port,
       po.nom_port,
       po.code_iso2_pays,
       COUNT(e.id_escale) AS nb_escales
FROM port po
INNER JOIN escale e ON po.id_port = e.id_port
GROUP BY po.id_port, po.nom_port, po.code_iso2_pays;
