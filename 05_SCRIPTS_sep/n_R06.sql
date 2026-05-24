
SELECT
    p.nom_port,
    p.code_iso2_pays             AS pays,
    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (
                (e.date_depart  + e.heure_depart)  -
                (e.date_arrivee + e.heure_arrivee)
            )) / 3600
        )::NUMERIC, 1
    )                            AS duree_moyenne_heures
FROM escale e
JOIN port p  ON e.id_port = p.id_port
WHERE e.date_depart   IS NOT NULL
  AND e.heure_depart  IS NOT NULL
  AND e.heure_arrivee IS NOT NULL
GROUP BY p.id_port, p.nom_port, p.code_iso2_pays
ORDER BY duree_moyenne_heures DESC;
