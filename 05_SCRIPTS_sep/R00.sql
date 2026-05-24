-- R00 
SELECT imo, nom_navire, annee_construction
FROM navire
WHERE annee_construction < 1995
ORDER BY annee_construction;