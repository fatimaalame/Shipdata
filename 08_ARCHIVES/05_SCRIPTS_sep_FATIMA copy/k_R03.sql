SELECT
    p.nom_port,
    p.code_iso2_pays          AS pays,
    p.taille_port,
    COUNT(e.id_escale)        AS nb_escales
FROM port p
JOIN escale e  ON e.id_port = p.id_port
GROUP BY p.id_port, p.nom_port, p.code_iso2_pays, p.taille_port
ORDER BY nb_escales DESC
LIMIT 5;