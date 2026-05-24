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
WHERE n.imo = (SELECT imo FROM navire WHERE nom_navire = 'MSC Beatrice')
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
    p.nom_port,
    p.code_iso2_pays             AS pays,
    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (
                (e.date_depart  + e.heure_depart)  -
                (e.date_arrivee + e.heure_arrivee)
            )) / 3600
        )::NUMERIC, 1
    )                            AS duree_moyenne_heures
FROM escale e
JOIN port p  ON e.id_port = p.id_port
WHERE e.date_depart   IS NOT NULL
  AND e.heure_depart  IS NOT NULL
  AND e.heure_arrivee IS NOT NULL
GROUP BY p.id_port, p.nom_port, p.code_iso2_pays
ORDER BY duree_moyenne_heures DESC;


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
    p.nom_pays                     AS pavillon,
    COUNT(n.imo)                   AS nb_navires,
    ROUND(AVG(n.gross_tonnage))    AS gross_tonnage_moyen,
    ROUND(AVG(n.deadweight_tonnage)) AS port_en_lourd_moyen
FROM pavillon p
JOIN navire n  ON n.id_pavillon = p.id_pavillon
GROUP BY p.id_pavillon, p.nom_pays
ORDER BY nb_navires DESC, gross_tonnage_moyen DESC;


-- R09 
SELECT
    n.nom_navire,
    t.nom_type,
    p.nom_pays                AS pavillon
FROM navire n
JOIN type_navire t  ON n.id_type_navire = t.id_type_navire
JOIN pavillon p     ON n.id_pavillon    = p.id_pavillon
WHERE NOT EXISTS (
    SELECT 1
    FROM escale e
    WHERE e.imo = n.imo
);


-- R10

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


-- R11 
SELECT
    pr.nom_proprietaire,
    pr.ville_siege,
    COUNT(n.imo)                                        AS nb_navires_actuels,
    SUM(n.gross_tonnage)                                AS tonnage_total,
    STRING_AGG(n.nom_navire, ', ' ORDER BY n.nom_navire) AS liste_navires
FROM proprietaire pr
JOIN propriete_navire pn  ON pn.id_proprietaire = pr.id_proprietaire
JOIN navire n             ON pn.imo             = n.imo
WHERE pn.date_fin IS NULL
GROUP BY pr.id_proprietaire, pr.nom_proprietaire, pr.ville_siege
HAVING COUNT(n.imo) > 1
ORDER BY nb_navires_actuels DESC, tonnage_total DESC;
