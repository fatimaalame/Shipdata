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