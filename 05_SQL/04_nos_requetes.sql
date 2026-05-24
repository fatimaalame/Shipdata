-- R00 
SELECT imo, nom_navire, annee_construction
FROM navire
WHERE annee_construction < 1995
ORDER BY annee_construction;


-- R01 
SELECT
    n.imo,
    n.nom_navire,
    t.nom_type                AS type_navire,
    c.nom_categorie           AS categorie,
    p.nom_pays                AS pavillon
FROM navire n
JOIN type_navire t            ON n.id_type_navire = t.id_type_navire
JOIN categorie_principale c   ON t.id_categorie   = c.id_categorie
JOIN pavillon p               ON n.id_pavillon     = p.id_pavillon
ORDER BY c.nom_categorie, t.nom_type, n.nom_navire;


-- R02 
SELECT
    c.nom_categorie,
    COUNT(n.imo)   AS nb_navires
FROM categorie_principale c
JOIN type_navire t  ON t.id_categorie   = c.id_categorie
JOIN navire n       ON n.id_type_navire = t.id_type_navire
GROUP BY c.id_categorie, c.nom_categorie
ORDER BY nb_navires DESC;


-- R03 
SELECT
    p.nom_port,
    p.code_iso2_pays          AS pays,
    p.taille_port,
    COUNT(e.id_escale)        AS nb_escales
FROM port p
JOIN escale e  ON e.id_port = p.id_port
GROUP BY p.id_port, p.nom_port, p.code_iso2_pays, p.taille_port
ORDER BY nb_escales DESC
LIMIT 5;


-- R04 
SELECT
    n.nom_navire,
    pr.nom_proprietaire,
    pn.date_debut,
    pn.date_fin,
    CASE
        WHEN pn.date_fin IS NULL THEN 'Propriétaire actuel'
        ELSE 'Ancien propriétaire'
    END                       AS statut
FROM propriete_navire pn
JOIN navire       n   ON pn.imo             = n.imo
JOIN proprietaire pr  ON pn.id_proprietaire = pr.id_proprietaire
WHERE n.imo = (SELECT imo FROM navire WHERE nom_navire = 'CHS ALPHA')
ORDER BY pn.date_debut;


-- R05
SELECT
    n.nom_navire,
    COUNT(pn.id_proprietaire)  AS nb_proprietaires
FROM navire n
JOIN propriete_navire pn  ON pn.imo = n.imo
GROUP BY n.imo, n.nom_navire
HAVING COUNT(pn.id_proprietaire) > 1
ORDER BY nb_proprietaires DESC;


-- R06 
SELECT
    p.nom_pays                       AS pavillon,
    COUNT(n.imo)                     AS nb_navires,
    ROUND(AVG(n.gross_tonnage))      AS gross_tonnage_moyen,
    ROUND(AVG(n.deadweight_tonnage)) AS port_en_lourd_moyen
FROM pavillon p
JOIN navire n  ON n.id_pavillon = p.id_pavillon
GROUP BY p.id_pavillon, p.nom_pays
ORDER BY nb_navires DESC, gross_tonnage_moyen DESC;


-- R07 
SELECT
    n.nom_navire,
    n.annee_construction,
    n.gross_tonnage,
    n.deadweight_tonnage,
    s.sigle                  AS societe_classification
FROM navire n
JOIN societe_classification s
    ON n.id_societe_classification = s.id_societe_classification
WHERE s.sigle = 'DNV'
ORDER BY n.gross_tonnage DESC;


-- R08 
SELECT
    t.nom_type,
    ROUND(AVG(2026 - n.annee_construction), 1) AS age_moyen
FROM navire n
JOIN type_navire t  ON n.id_type_navire = t.id_type_navire
GROUP BY t.nom_type
ORDER BY age_moyen DESC;


-- R09 
SELECT
    c.nom_categorie,
    n.nom_navire,
    n.gross_tonnage,
    RANK() OVER (
        PARTITION BY c.id_categorie
        ORDER BY n.gross_tonnage DESC
    )                         AS rang_dans_categorie
FROM navire n
JOIN type_navire t            ON n.id_type_navire = t.id_type_navire
JOIN categorie_principale c   ON t.id_categorie   = c.id_categorie
ORDER BY c.nom_categorie, rang_dans_categorie;


-- R10 
SELECT
    po.nom_port,
    po.code_iso2_pays         AS pays,
    e.date_arrivee,
    e.date_depart
FROM escale e
JOIN navire n   ON e.imo      = n.imo
JOIN port po    ON e.id_port  = po.id_port
WHERE n.nom_navire = 'NIVIN'
ORDER BY e.date_arrivee;


-- R11
SELECT
    n.nom_navire,
    e.date_arrivee,
    e.date_depart
FROM escale e
JOIN navire n   ON e.imo     = n.imo
JOIN port po    ON e.id_port = po.id_port
WHERE po.nom_port = 'Savona'
  AND e.date_arrivee BETWEEN '2023-04-15' AND '2023-04-18'
ORDER BY e.date_arrivee;


-- R12 
SELECT
    n.nom_navire,
    pr.nom_proprietaire,
    pr.code_iso2_pays,
    pr.annee_creation,
    pn.date_debut,
    pn.date_fin
FROM propriete_navire pn
JOIN navire       n   ON pn.imo             = n.imo
JOIN proprietaire pr  ON pn.id_proprietaire = pr.id_proprietaire
WHERE n.imo = 8206533
ORDER BY pn.date_debut;

-- R13 
SELECT
    p.nom_pays                AS pavillon,
    COUNT(n.imo)              AS nb_navires
FROM navire n
JOIN pavillon p  ON n.id_pavillon = p.id_pavillon
GROUP BY p.nom_pays
ORDER BY nb_navires DESC;