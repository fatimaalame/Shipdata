SELECT 'categorie_principale' AS table_name, COUNT(*) FROM categorie_principale
UNION ALL
SELECT 'type_navire', COUNT(*) FROM type_navire
UNION ALL
SELECT 'pavillon', COUNT(*) FROM pavillon
UNION ALL
SELECT 'societe_classification', COUNT(*) FROM societe_classification
UNION ALL
SELECT 'port', COUNT(*) FROM port
UNION ALL
SELECT 'constructeur', COUNT(*) FROM constructeur
UNION ALL
SELECT 'proprietaire', COUNT(*) FROM proprietaire
UNION ALL
SELECT 'navire', COUNT(*) FROM navire
UNION ALL
SELECT 'propriete_navire', COUNT(*) FROM propriete_navire
UNION ALL
SELECT 'escale', COUNT(*) FROM escale;