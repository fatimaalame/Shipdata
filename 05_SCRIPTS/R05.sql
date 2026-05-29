-- R05
SELECT
    n.nom_navire,
    COUNT(pn.id_proprietaire)  AS nb_proprietaires
FROM navire n
JOIN propriete_navire pn  ON pn.imo = n.imo
GROUP BY n.imo, n.nom_navire
HAVING COUNT(pn.id_proprietaire) > 1
ORDER BY nb_proprietaires DESC;