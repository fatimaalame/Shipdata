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

