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