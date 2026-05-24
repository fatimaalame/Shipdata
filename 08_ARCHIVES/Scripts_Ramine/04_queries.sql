SELECT tn.nom_type, COUNT(n.imo) AS nb_navires
FROM navire n
INNER JOIN type_navire tn ON n.id_type_navire = tn.id_type_navire
GROUP BY tn.nom_type
ORDER BY nb_navires DESC;

SELECT imo, nom_navire, annee_construction
FROM navire
WHERE annee_construction < 1995
ORDER BY annee_construction;

SELECT tn.nom_type, ROUND(AVG(2026 - n.annee_construction), 1) AS age_moyen
FROM navire n
INNER JOIN type_navire tn ON n.id_type_navire = tn.id_type_navire
GROUP BY tn.nom_type
ORDER BY age_moyen DESC;

SELECT p.nom_pays, COUNT(n.imo) AS nb_navires
FROM navire n
INNER JOIN pavillon p ON n.id_pavillon = p.id_pavillon
GROUP BY p.nom_pays
ORDER BY nb_navires DESC;

SELECT imo, nom_navire, gross_tonnage
FROM navire
ORDER BY gross_tonnage DESC
LIMIT 5;

SELECT n.imo, n.nom_navire, n.annee_construction
FROM navire n
INNER JOIN societe_classification sc ON n.id_societe_classification = sc.id_societe_classification
WHERE sc.sigle = 'RINA';

SELECT c.nom_constructeur, COUNT(n.imo) AS nb_navires
FROM navire n
INNER JOIN constructeur c ON n.id_constructeur = c.id_constructeur
GROUP BY c.nom_constructeur
HAVING COUNT(n.imo) >= 2
ORDER BY nb_navires DESC;

SELECT pr.nom_proprietaire, COUNT(DISTINCT pn.imo) AS nb_navires
FROM propriete_navire pn
INNER JOIN proprietaire pr ON pn.id_proprietaire = pr.id_proprietaire
GROUP BY pr.nom_proprietaire
HAVING COUNT(DISTINCT pn.imo) >= 2
ORDER BY nb_navires DESC;

SELECT po.nom_port, po.code_iso2_pays, e.date_arrivee, e.date_depart
FROM escale e
INNER JOIN navire n ON e.imo = n.imo
INNER JOIN port po ON e.id_port = po.id_port
WHERE n.nom_navire = 'NIVIN'
ORDER BY e.date_arrivee;

SELECT pr.nom_proprietaire, pn.date_debut, pn.date_fin
FROM propriete_navire pn
INNER JOIN navire n ON pn.imo = n.imo
INNER JOIN proprietaire pr ON pn.id_proprietaire = pr.id_proprietaire
WHERE n.nom_navire = 'NIVIN'
ORDER BY pn.date_debut;

SELECT n.nom_navire, e.date_arrivee, e.date_depart
FROM escale e
INNER JOIN navire n ON e.imo = n.imo
INNER JOIN port po ON e.id_port = po.id_port
WHERE po.nom_port = 'Savona'
  AND e.date_arrivee BETWEEN '2023-04-15' AND '2023-04-18 23:59:59'
ORDER BY e.date_arrivee;

SELECT p.nom_pays, COUNT(n.imo) AS nb_navires, ROUND(AVG(n.gross_tonnage), 0) AS tonnage_moyen
FROM navire n
INNER JOIN pavillon p ON n.id_pavillon = p.id_pavillon
GROUP BY p.nom_pays
ORDER BY tonnage_moyen DESC;

