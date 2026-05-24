# ShipData - Interface Streamlit
# Interface prototype qui lit directement les fichiers CSV du projet

from pathlib import Path

import pandas as pd
import streamlit as st


# -----------------------------
# Configuration de la page
# -----------------------------

st.set_page_config(
    page_title="ShipData",
    page_icon="🚢",
    layout="wide"
)


# -----------------------------
# Style CSS
# -----------------------------

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f7fb;
    }

    .main-header {
        background-color: #0f172a;
        padding: 28px 35px;
        border-radius: 0px 0px 18px 18px;
        margin-bottom: 30px;
    }

    .main-title {
        color: white;
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .main-subtitle {
        color: #cbd5e1;
        font-size: 16px;
    }

    .card {
        background-color: white;
        padding: 24px;
        border-radius: 18px;
        box-shadow: 0px 8px 25px rgba(15, 23, 42, 0.08);
        min-height: 120px;
    }

    .card-label {
        color: #64748b;
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .card-value {
        color: #0f172a;
        font-size: 34px;
        font-weight: 800;
    }

    .card-caption {
        color: #16a34a;
        font-size: 14px;
        margin-top: 6px;
        font-weight: 600;
    }

    .section-box {
        background-color: white;
        padding: 28px;
        border-radius: 18px;
        box-shadow: 0px 8px 25px rgba(15, 23, 42, 0.08);
        margin-top: 25px;
    }

    .section-title {
        color: #111827;
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 20px;
    }

    .sql-box {
        background-color: #0f172a;
        color: #e5e7eb;
        padding: 22px;
        border-radius: 12px;
        font-family: monospace;
        white-space: pre-wrap;
        font-size: 14px;
        line-height: 1.55;
    }

    div[data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 12px;
    }

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        margin-top: 35px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Chargement des CSV
# -----------------------------

@st.cache_data
def load_data():
    # Le fichier Streamlit est dans 07_RAPPORT_FINAL, donc on remonte d'un dossier
    base_dir = Path(__file__).resolve().parents[1]

    # Selon l'organisation du projet, les CSV peuvent être dans Data ou dans 02_DONNEES
    possible_data_dirs = [
        base_dir / "Data",
        base_dir / "02_DONNEES",
        base_dir / "02_DONNEES" / "Data",
    ]

    data_dir = None
    for folder in possible_data_dirs:
        if (folder / "01_categorie_principale.csv").exists():
            data_dir = folder
            break

    if data_dir is None:
        st.error("Impossible de trouver le dossier contenant les fichiers CSV")
        st.write("Dossiers testés :")
        for folder in possible_data_dirs:
            st.write(str(folder))
        st.stop()

    def read_csv_safe(filename):
        # Certains CSV peuvent contenir des caractères spéciaux encodés différemment
        file_path = data_dir / filename
        try:
            return pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding="latin1")

    categorie = read_csv_safe("01_categorie_principale.csv")
    type_navire = read_csv_safe("02_type_navires.csv")
    pavillon = read_csv_safe("03_pavillons.csv")
    societe = read_csv_safe("04_societes_classification.csv")
    port = read_csv_safe("05_port_data.csv")
    constructeur = read_csv_safe("06_constructeurs.csv")
    proprietaire = read_csv_safe("07_proprietaires.csv")
    navire = read_csv_safe("08_navires.csv")
    propriete_navire = read_csv_safe("09_propriete_navire.csv")
    escale = read_csv_safe("10_escales.csv")

    return {
        "categorie": categorie,
        "type_navire": type_navire,
        "pavillon": pavillon,
        "societe": societe,
        "port": port,
        "constructeur": constructeur,
        "proprietaire": proprietaire,
        "navire": navire,
        "propriete_navire": propriete_navire,
        "escale": escale,
    }


data = load_data()

categorie = data["categorie"]
type_navire = data["type_navire"]
pavillon = data["pavillon"]
societe = data["societe"]
port = data["port"]
constructeur = data["constructeur"]
proprietaire = data["proprietaire"]
navire = data["navire"]
propriete_navire = data["propriete_navire"]
escale = data["escale"]


# -----------------------------
# Préparation d'une vue principale
# -----------------------------

current_owner = propriete_navire[propriete_navire["date_fin"].isna()].copy()

ships_view = (
    navire
    .merge(type_navire[["id_type_navire", "nom_type", "id_categorie"]], on="id_type_navire", how="left")
    .merge(categorie[["id_categorie", "nom_categorie"]], on="id_categorie", how="left")
    .merge(pavillon[["id_pavillon", "nom_pays"]], on="id_pavillon", how="left")
    .merge(societe[["id_societe_classification", "nom_societe"]], on="id_societe_classification", how="left")
    .merge(constructeur[["id_constructeur", "nom_constructeur"]], on="id_constructeur", how="left")
    .merge(current_owner[["imo", "id_proprietaire", "date_debut"]], on="imo", how="left")
    .merge(proprietaire[["id_proprietaire", "nom_proprietaire", "code_iso2_pays"]], on="id_proprietaire", how="left")
)


# -----------------------------
# Header
# -----------------------------

st.markdown(
    """
    <div class="main-header">
        <div class="main-title">ShipData</div>
        <div class="main-subtitle">Interface prototype de consultation des navires, propriétaires, pavillons, ports et escales</div>
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Statistiques rapides
# -----------------------------

nb_navires = len(navire)
nb_pavillons = len(pavillon)
nb_ports = len(port)
nb_societes = len(societe)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-label">Navires enregistrés</div>
            <div class="card-value">{nb_navires}</div>
            <div class="card-caption">données IMO</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-label">Pavillons représentés</div>
            <div class="card-value">{nb_pavillons}</div>
            <div class="card-caption">pays disponibles</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-label">Ports suivis</div>
            <div class="card-value">{nb_ports}</div>
            <div class="card-caption">ports dans la base</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="card">
            <div class="card-label">Sociétés de classification</div>
            <div class="card-value">{nb_societes}</div>
            <div class="card-caption">BV, DNV, ABS...</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------
# Recherche multicritère
# -----------------------------

st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Recherche multicritère</div>', unsafe_allow_html=True)

types = sorted(type_navire["nom_type"].dropna().unique().tolist())
pavillons = sorted(pavillon["nom_pays"].dropna().unique().tolist())
societes = sorted(societe["nom_societe"].dropna().unique().tolist())

c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

with c1:
    search_text = st.text_input("Rechercher par nom ou numéro IMO", placeholder="Exemple : NIVIN ou 8206533")

with c2:
    selected_type = st.selectbox("Type de navire", ["Tous"] + types)

with c3:
    selected_pavillon = st.selectbox("Pavillon", ["Tous"] + pavillons)

with c4:
    selected_societe = st.selectbox("Société de classification", ["Toutes"] + societes)

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Résultats de recherche
# -----------------------------

filtered = ships_view.copy()

if search_text:
    search_lower = search_text.lower()
    filtered = filtered[
        filtered["nom_navire"].astype(str).str.lower().str.contains(search_lower, na=False)
        | filtered["imo"].astype(str).str.contains(search_text, na=False)
    ]

if selected_type != "Tous":
    filtered = filtered[filtered["nom_type"] == selected_type]

if selected_pavillon != "Tous":
    filtered = filtered[filtered["nom_pays"] == selected_pavillon]

if selected_societe != "Toutes":
    filtered = filtered[filtered["nom_societe"] == selected_societe]

results = filtered[[
    "imo",
    "nom_navire",
    "nom_type",
    "annee_construction",
    "nom_pays",
    "gross_tonnage",
    "deadweight_tonnage",
    "longueur_m",
    "nom_societe",
    "nom_proprietaire",
]].rename(columns={
    "imo": "IMO",
    "nom_navire": "Nom du navire",
    "nom_type": "Type",
    "annee_construction": "Année",
    "nom_pays": "Pavillon",
    "gross_tonnage": "GT",
    "deadweight_tonnage": "DWT",
    "longueur_m": "Longueur",
    "nom_societe": "Classification",
    "nom_proprietaire": "Propriétaire actuel",
})

st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Résultats de recherche</div>', unsafe_allow_html=True)
st.dataframe(results, use_container_width=True, hide_index=True)
st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Requêtes SQL disponibles
# -----------------------------

queries = {
    "1. Afficher les navires les plus anciens": """
SELECT
    n.nom_navire,
    n.annee_construction,
    p.nom_pays AS pavillon,
    t.nom_type AS type_navire,
    sc.nom_societe AS classification
FROM navire n
JOIN pavillon p ON n.id_pavillon = p.id_pavillon
JOIN type_navire t ON n.id_type_navire = t.id_type_navire
JOIN societe_classification sc ON n.id_societe_classification = sc.id_societe_classification
ORDER BY n.annee_construction ASC
LIMIT 10;
""",

    "2. Comparer le tonnage moyen par type de navire": """
SELECT
    t.nom_type,
    COUNT(n.imo) AS nombre_navires,
    ROUND(AVG(n.gross_tonnage), 2) AS tonnage_moyen
FROM navire n
JOIN type_navire t ON n.id_type_navire = t.id_type_navire
GROUP BY t.nom_type
ORDER BY tonnage_moyen DESC;
""",

    "3. Trouver les pavillons les plus représentés": """
SELECT
    p.nom_pays,
    COUNT(n.imo) AS nombre_navires
FROM navire n
JOIN pavillon p ON n.id_pavillon = p.id_pavillon
GROUP BY p.nom_pays
ORDER BY nombre_navires DESC;
""",

    "4. Lister les propriétaires possédant plusieurs navires": """
SELECT
    pr.nom_proprietaire,
    COUNT(n.imo) AS nombre_navires
FROM proprietaire pr
JOIN propriete_navire pn ON pr.id_proprietaire = pn.id_proprietaire
JOIN navire n ON pn.imo = n.imo
WHERE pn.date_fin IS NULL
GROUP BY pr.nom_proprietaire
HAVING COUNT(n.imo) > 1
ORDER BY nombre_navires DESC;
""",

    "5. Identifier les constructeurs les plus fréquents": """
SELECT
    c.nom_constructeur,
    COUNT(n.imo) AS nombre_navires
FROM constructeur c
JOIN navire n ON c.id_constructeur = n.id_constructeur
GROUP BY c.nom_constructeur
ORDER BY nombre_navires DESC;
""",

    "6. Rechercher les navires classés par Bureau Veritas": """
SELECT
    n.nom_navire,
    t.nom_type,
    n.gross_tonnage,
    sc.nom_societe
FROM navire n
JOIN type_navire t ON n.id_type_navire = t.id_type_navire
JOIN societe_classification sc ON n.id_societe_classification = sc.id_societe_classification
WHERE sc.nom_societe = 'Bureau Veritas'
ORDER BY n.gross_tonnage DESC;
""",

    "7. Calculer l'âge moyen des navires par pavillon": """
SELECT
    p.nom_pays AS pavillon,
    ROUND(AVG(2026 - n.annee_construction), 2) AS age_moyen
FROM navire n
JOIN pavillon p ON n.id_pavillon = p.id_pavillon
GROUP BY p.nom_pays
ORDER BY age_moyen DESC;
""",

    "8. Trouver les navires avec le plus grand DWT": """
SELECT
    nom_navire,
    deadweight_tonnage,
    gross_tonnage,
    longueur_m
FROM navire
ORDER BY deadweight_tonnage DESC
LIMIT 10;
""",

    "9. Historique des propriétaires de NIVIN": """
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
""",

    "10. Ports les plus fréquentés": """
SELECT
    p.nom_port,
    p.code_iso2_pays,
    COUNT(e.id_escale) AS nombre_escales
FROM port p
JOIN escale e ON p.id_port = e.id_port
GROUP BY p.nom_port, p.code_iso2_pays
ORDER BY nombre_escales DESC
LIMIT 10;
"""
}

st.markdown('<div class="section-box">', unsafe_allow_html=True)
left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="section-title">Requêtes SQL disponibles</div>', unsafe_allow_html=True)
    selected_query = st.radio(
        "Choisir une requête",
        list(queries.keys()),
        label_visibility="collapsed"
    )

with right:
    st.markdown('<div class="section-title">Aperçu SQL</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="sql-box">{queries[selected_query]}</div>
        """,
        unsafe_allow_html=True
    )

st.info("Cette interface est un prototype de consultation. Elle lit les fichiers CSV du projet et affiche les requêtes SQL prévues pour la base PostgreSQL")

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Footer
# -----------------------------

st.markdown(
    """
    <div class="footer">
        Projet de bases de données — ShipData — Interface prototype Streamlit
    </div>
    """,
    unsafe_allow_html=True
)