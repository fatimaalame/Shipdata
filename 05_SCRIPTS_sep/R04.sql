-- R04 
SELECT
    n.nom_navire,
    pr.nom_proprietaire,
    pn.date_debut,
    pn.date_fin,
    CASE
        WHEN pn.date_fin IS NULL THEN 'Propriétaire actuel'
        ELSE 'Ancien propriétaire'
    END                       AS statut
FROM propriete_navire pn
JOIN navire       n   ON pn.imo             = n.imo
JOIN proprietaire pr  ON pn.id_proprietaire = pr.id_proprietaire
WHERE n.imo = (SELECT imo FROM navire WHERE nom_navire = 'CHS ALPHA')
ORDER BY pn.date_debut;