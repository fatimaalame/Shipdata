-- R08 
SELECT
    t.nom_type,
    ROUND(AVG(2026 - n.annee_construction), 1) AS age_moyen
FROM navire n
JOIN type_navire t  ON n.id_type_navire = t.id_type_navire
GROUP BY t.nom_type
ORDER BY age_moyen DESC;