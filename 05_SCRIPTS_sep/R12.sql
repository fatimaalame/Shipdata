-- R12 
SELECT
    n.nom_navire,
    pr.nom_proprietaire,
    pr.code_iso2_pays,
    pr.annee_creation,
    pn.date_debut,
    pn.date_fin
FROM propriete_navire pn
JOIN navire       n   ON pn.imo             = n.imo
JOIN proprietaire pr  ON pn.id_proprietaire = pr.id_proprietaire
WHERE n.imo = 8206533
ORDER BY pn.date_debut;