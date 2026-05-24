UPDATE proprietaire
SET nom_proprietaire = 'ALAME Export SA',
    code_iso2_pays = 'PA',
    annee_creation = 2005,
    ville_siege = 'Panama City'
WHERE id_proprietaire = 7;

UPDATE propriete_navire
SET date_fin = '2011-09-16'
WHERE imo = 8206533
  AND id_proprietaire = 14
  AND date_debut = '2005-09-01';

UPDATE propriete_navire
SET date_debut = '2011-09-17'
WHERE imo = 8206533
  AND id_proprietaire = 7
  AND date_fin IS NULL;