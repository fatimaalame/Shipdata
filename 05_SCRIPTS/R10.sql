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
