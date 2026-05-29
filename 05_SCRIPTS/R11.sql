-- R11
SELECT
    n.nom_navire,
    e.date_arrivee,
    e.date_depart
FROM escale e
JOIN navire n   ON e.imo     = n.imo
JOIN port po    ON e.id_port = po.id_port
WHERE po.nom_port = 'Savona'
  AND e.date_arrivee BETWEEN '2023-04-15' AND '2023-04-18'
ORDER BY e.date_arrivee;