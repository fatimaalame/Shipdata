SELECT n.imo, n.nom_navire
FROM navire n
LEFT JOIN type_navire t ON n.id_type_navire = t.id_type_navire
WHERE t.id_type_navire IS NULL;