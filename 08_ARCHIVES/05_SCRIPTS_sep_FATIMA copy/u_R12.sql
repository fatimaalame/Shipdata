SELECT
    n.nom_navire,
    p.nom_proprietaire,
    p.code_iso2_pays,
    p.annee_creation,
    pn.date_debut,
    pn.date_fin
FROM propriete_navire pn
JOIN navire n ON pn.imo = n.imo
JOIN proprietaire p ON pn.id_proprietaire = p.id_proprietaire
WHERE n.imo = 8206533
ORDER BY pn.date_debut;