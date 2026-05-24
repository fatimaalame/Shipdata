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