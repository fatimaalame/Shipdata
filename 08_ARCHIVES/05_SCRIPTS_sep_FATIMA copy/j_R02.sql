SELECT
    c.nom_categorie,
    COUNT(n.imo)   AS nb_navires
FROM categorie_principale c
JOIN type_navire t  ON t.id_categorie   = c.id_categorie
JOIN navire n       ON n.id_type_navire = t.id_type_navire
GROUP BY c.id_categorie, c.nom_categorie
ORDER BY nb_navires DESC;