-- R13 
SELECT
    p.nom_pays                AS pavillon,
    COUNT(n.imo)              AS nb_navires
FROM navire n
JOIN pavillon p  ON n.id_pavillon = p.id_pavillon
GROUP BY p.nom_pays
ORDER BY nb_navires DESC;