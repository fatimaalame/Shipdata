# ============================================================
# ShipData - Interface Streamlit moderne
# Projet de base de données
# ============================================================
# Lancement :
# streamlit run 07_RAPPORT_FINAL/INTERFACE/interface_shipdata.py
#
# Dépendances :
# pip install streamlit pandas psycopg2-binary
# ============================================================

from pathlib import Path
import json
import unicodedata
from datetime import date

import pandas as pd
import psycopg2
import streamlit as st


# ------------------------------------------------------------
# Configuration de la page
# ------------------------------------------------------------

st.set_page_config(
    page_title="ShipData",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ------------------------------------------------------------
# Chemins
# ------------------------------------------------------------
# Le fichier Streamlit est dans 07_RAPPORT_FINAL/INTERFACE.
# parents[2] remonte à la racine du projet Shipdata.
ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.json"


# ------------------------------------------------------------
# CSS : style proche de ton exemple HTML/CSS
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    /* Cache les éléments Streamlit inutiles */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    :root {
        --navy: #0f172a;
        --bg: #f4f7fb;
        --card: #ffffff;
        --text: #1f2937;
        --muted: #6b7280;
        --blue: #0ea5e9;
        --green: #16a34a;
        --line: #e5e7eb;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .block-container {
        padding-top: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }

    .main-content {
        padding: 2.2rem 2.6rem 3rem 2.6rem;
    }

    .topbar {
        background: var(--navy);
        color: white;
        padding: 1.25rem 2.6rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.15);
    }

    .brand-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.05;
    }

    .brand-subtitle {
        color: #cbd5e1;
        font-size: 0.92rem;
        margin-top: 0.25rem;
    }

    .nav-links {
        display: flex;
        gap: 2rem;
        font-weight: 700;
        font-size: 0.95rem;
        color: #e5e7eb;
    }

    .nav-links span {
        opacity: 0.92;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 850;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }

    .hero-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.8rem;
    }

    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem 1.65rem;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
        border: 1px solid rgba(229, 231, 235, 0.75);
        min-height: 128px;
    }

    .metric-label {
        color: #6b7280;
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.55rem;
    }

    .metric-value {
        color: #111827;
        font-size: 2rem;
        font-weight: 850;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem;
    }

    .metric-note {
        color: #16a34a;
        font-weight: 700;
        font-size: 0.9rem;
    }

    .panel {
        background: white;
        border-radius: 16px;
        padding: 1.7rem;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.07);
        border: 1px solid rgba(229, 231, 235, 0.75);
        margin-top: 1.6rem;
    }

    .panel-title {
        font-size: 1.45rem;
        font-weight: 850;
        color: #1f2937;
        margin-bottom: 1rem;
    }

    .sql-box {
        background: #0b1020;
        color: #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        font-family: "SF Mono", Consolas, monospace;
        font-size: 0.86rem;
        line-height: 1.55;
        white-space: pre-wrap;
        overflow-x: auto;
        min-height: 430px;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
    }

    .query-item {
        background: #f3f6fb;
        padding: 0.85rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        font-weight: 650;
        color: #273244;
        border: 1px solid #eef2f7;
    }

    .result-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.92rem;
        overflow: hidden;
    }

    .result-table th {
        text-align: left;
        background: #eef3fb;
        padding: 0.9rem;
        color: #374151;
        font-weight: 800;
        border-bottom: 1px solid #dbe3ef;
    }

    .result-table td {
        padding: 0.85rem 0.9rem;
        border-bottom: 1px solid #eef2f7;
        color: #374151;
    }

    .badge-type {
        display: inline-block;
        background: #dff4ff;
        color: #0077a8;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.78rem;
    }

    .badge-year-old {
        display: inline-block;
        background: #ffe4ec;
        color: #be123c;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.78rem;
    }

    .badge-year {
        display: inline-block;
        color: #374151;
        font-weight: 700;
    }

    div.stButton > button:first-child {
        background: #0ea5e9;
        color: white;
        border: 0;
        border-radius: 10px;
        padding: 0.65rem 1.1rem;
        font-weight: 800;
        box-shadow: 0 8px 18px rgba(14,165,233,0.22);
    }

    div.stButton > button:first-child:hover {
        background: #0284c7;
        color: white;
        border: 0;
    }

    div[data-testid="stSelectbox"] > div,
    div[data-testid="stTextInput"] > div {
        border-radius: 10px;
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.9rem;
    }

    .section-separator {
        height: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Petites fonctions utiles
# ------------------------------------------------------------

def normalize(text):
    """Simplifie un texte pour comparer les noms de colonnes plus facilement."""
    if text is None:
        return ""
    text = str(text).lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace(" ", "_").replace("-", "_")
    return text


def read_config():
    """Lit config.json."""
    if not CONFIG_PATH.exists():
        st.error(f"Fichier config.json introuvable à la racine du projet : {CONFIG_PATH}")
        st.stop()

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_resource(show_spinner=False)
def get_connection():
    """Crée la connexion PostgreSQL."""
    config = read_config()
    return psycopg2.connect(
        host=config.get("host", "localhost"),
        port=config.get("port", 5432),
        user=config.get("user", "postgres"),
        password=config.get("password", ""),
        database=config.get("database", "shipdata")
    )


def run_query(sql, params=None):
    """Exécute une requête SQL et renvoie un DataFrame."""
    conn = get_connection()
    return pd.read_sql_query(sql, conn, params=params)


@st.cache_data(show_spinner=False)
def get_tables():
    """Récupère les tables visibles dans public."""
    sql = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """
    return run_query(sql)["table_name"].tolist()


def find_table(candidates):
    """Trouve une table même si son nom a une casse différente."""
    tables = get_tables()
    normalized = {normalize(t): t for t in tables}

    for candidate in candidates:
        key = normalize(candidate)
        if key in normalized:
            return normalized[key]

    for candidate in candidates:
        key = normalize(candidate)
        for norm_name, real_name in normalized.items():
            if key in norm_name or norm_name in key:
                return real_name

    return None


@st.cache_data(show_spinner=False)
def get_columns(table_name):
    """Récupère les colonnes d'une table."""
    sql = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position;
    """
    return run_query(sql, (table_name,))["column_name"].tolist()


def find_column(table_name, candidates):
    """Trouve une colonne même si le nom n'est pas exactement identique."""
    if table_name is None:
        return None

    columns = get_columns(table_name)
    normalized = {normalize(c): c for c in columns}

    for candidate in candidates:
        key = normalize(candidate)
        if key in normalized:
            return normalized[key]

    for candidate in candidates:
        key = normalize(candidate)
        for norm_name, real_name in normalized.items():
            if key in norm_name or norm_name in key:
                return real_name

    return None


def q(name):
    """Ajoute des guillemets SQL autour d'un nom de table/colonne."""
    return '"' + str(name).replace('"', '""') + '"'


def first_existing_table(*candidate_groups):
    for candidates in candidate_groups:
        table = find_table(candidates)
        if table:
            return table
    return None


# ------------------------------------------------------------
# Détection du modèle
# ------------------------------------------------------------

def detect_context():
    """Détecte les tables et colonnes principales du projet ShipData."""
    navire_table = find_table(["navire", "navires", "vessel", "vessels"])
    type_table = find_table(["type_navire", "typenavire", "type navire", "vessel_type"])
    pavillon_table = find_table(["pavillon", "pays_pavillon", "flag"])
    classification_table = find_table(["societe_classification", "societeclassification", "classification"])
    proprietaire_table = find_table(["proprietaire", "owner"])
    constructeur_table = find_table(["constructeur", "builder"])
    port_table = find_table(["port", "ports"])
    escale_table = find_table(["escale", "escales"])

    ctx = {
        "navire": navire_table,
        "type": type_table,
        "pavillon": pavillon_table,
        "classification": classification_table,
        "proprietaire": proprietaire_table,
        "constructeur": constructeur_table,
        "port": port_table,
        "escale": escale_table,
    }

    if navire_table:
        ctx.update({
            "imo": find_column(navire_table, ["imo", "numero_imo", "imo_number", "num_imo"]),
            "nom_navire": find_column(navire_table, ["nom_navire", "nom", "name", "vessel_name"]),
            "annee": find_column(navire_table, ["annee_construction", "annee", "year_built", "construction_year"]),
            "gt": find_column(navire_table, ["gt", "gross_tonnage", "tonnage_brut"]),
            "dwt": find_column(navire_table, ["dwt", "deadweight", "deadweight_tonnage"]),
            "longueur": find_column(navire_table, ["longueur", "length", "loa"]),
            "id_type": find_column(navire_table, ["id_type", "id_type_navire", "type_id"]),
            "id_pavillon": find_column(navire_table, ["id_pavillon", "pavillon_id", "id_flag"]),
            "id_classification": find_column(navire_table, ["id_classification", "id_societe_classification", "classification_id"]),
            "id_proprietaire": find_column(navire_table, ["id_proprietaire", "proprietaire_id", "owner_id"]),
            "id_constructeur": find_column(navire_table, ["id_constructeur", "constructeur_id", "builder_id"]),
        })

    if type_table:
        ctx.update({
            "type_id": find_column(type_table, ["id_type", "id_type_navire", "id"]),
            "type_name": find_column(type_table, ["nom_type", "type_navire", "libelle", "nom", "type"]),
        })

    if pavillon_table:
        ctx.update({
            "pavillon_id": find_column(pavillon_table, ["id_pavillon", "id", "pavillon_id"]),
            "pavillon_name": find_column(pavillon_table, ["nom_pays", "pays", "nom_pavillon", "pavillon", "country", "flag"]),
        })

    if classification_table:
        ctx.update({
            "classification_id": find_column(classification_table, ["id_classification", "id_societe_classification", "id"]),
            "classification_name": find_column(classification_table, ["nom_societe", "nom_classification", "societe", "classification", "nom"]),
        })

    if proprietaire_table:
        ctx.update({
            "proprietaire_id": find_column(proprietaire_table, ["id_proprietaire", "id"]),
            "proprietaire_name": find_column(proprietaire_table, ["nom_proprietaire", "proprietaire", "owner", "nom"]),
        })

    if constructeur_table:
        ctx.update({
            "constructeur_id": find_column(constructeur_table, ["id_constructeur", "id"]),
            "constructeur_name": find_column(constructeur_table, ["nom_constructeur", "constructeur", "builder", "nom"]),
        })

    if port_table:
        ctx.update({
            "port_id": find_column(port_table, ["id_port", "id"]),
            "port_name": find_column(port_table, ["nom_port", "port", "nom"]),
            "port_country": find_column(port_table, ["pays", "country", "nom_pays"]),
        })

    return ctx


# ------------------------------------------------------------
# Construction SQL
# ------------------------------------------------------------

def build_main_query(ctx, search_text="", type_filter="Type de navire", pavillon_filter="Pavillon", class_filter="Société de classification"):
    """Construit la requête principale de recherche."""
    n = ctx["navire"]
    if not n:
        return None, []

    select_parts = []
    joins = []
    where_parts = []
    params = []

    # Colonnes principales
    imo_col = ctx.get("imo")
    name_col = ctx.get("nom_navire")
    year_col = ctx.get("annee")
    gt_col = ctx.get("gt")
    dwt_col = ctx.get("dwt")
    length_col = ctx.get("longueur")

    select_parts.append(f"n.{q(imo_col)} AS imo" if imo_col else "NULL AS imo")
    select_parts.append(f"n.{q(name_col)} AS nom_navire" if name_col else "NULL AS nom_navire")

    # Type
    if ctx.get("type") and ctx.get("id_type") and ctx.get("type_id") and ctx.get("type_name"):
        joins.append(f"LEFT JOIN {q(ctx['type'])} t ON n.{q(ctx['id_type'])} = t.{q(ctx['type_id'])}")
        select_parts.append(f"t.{q(ctx['type_name'])} AS type_navire")
    else:
        select_parts.append("NULL AS type_navire")

    select_parts.append(f"n.{q(year_col)} AS annee_construction" if year_col else "NULL AS annee_construction")

    # Pavillon
    if ctx.get("pavillon") and ctx.get("id_pavillon") and ctx.get("pavillon_id") and ctx.get("pavillon_name"):
        joins.append(f"LEFT JOIN {q(ctx['pavillon'])} p ON n.{q(ctx['id_pavillon'])} = p.{q(ctx['pavillon_id'])}")
        select_parts.append(f"p.{q(ctx['pavillon_name'])} AS pavillon")
    else:
        select_parts.append("NULL AS pavillon")

    select_parts.append(f"n.{q(gt_col)} AS gt" if gt_col else "NULL AS gt")
    select_parts.append(f"n.{q(dwt_col)} AS dwt" if dwt_col else "NULL AS dwt")
    select_parts.append(f"n.{q(length_col)} AS longueur" if length_col else "NULL AS longueur")

    # Classification
    if ctx.get("classification") and ctx.get("id_classification") and ctx.get("classification_id") and ctx.get("classification_name"):
        joins.append(f"LEFT JOIN {q(ctx['classification'])} c ON n.{q(ctx['id_classification'])} = c.{q(ctx['classification_id'])}")
        select_parts.append(f"c.{q(ctx['classification_name'])} AS classification")
    else:
        select_parts.append("NULL AS classification")

    # Propriétaire
    if ctx.get("proprietaire") and ctx.get("id_proprietaire") and ctx.get("proprietaire_id") and ctx.get("proprietaire_name"):
        joins.append(f"LEFT JOIN {q(ctx['proprietaire'])} pr ON n.{q(ctx['id_proprietaire'])} = pr.{q(ctx['proprietaire_id'])}")
        select_parts.append(f"pr.{q(ctx['proprietaire_name'])} AS proprietaire")
    else:
        select_parts.append("NULL AS proprietaire")

    # Recherche texte
    if search_text.strip():
        search_value = f"%{search_text.strip()}%"
        text_conditions = []
        if name_col:
            text_conditions.append(f"CAST(n.{q(name_col)} AS TEXT) ILIKE %s")
            params.append(search_value)
        if imo_col:
            text_conditions.append(f"CAST(n.{q(imo_col)} AS TEXT) ILIKE %s")
            params.append(search_value)
        if text_conditions:
            where_parts.append("(" + " OR ".join(text_conditions) + ")")

    # Filtres
    if type_filter != "Type de navire" and "t." in " ".join(joins) and ctx.get("type_name"):
        where_parts.append(f"t.{q(ctx['type_name'])} = %s")
        params.append(type_filter)

    if pavillon_filter != "Pavillon" and "p." in " ".join(joins) and ctx.get("pavillon_name"):
        where_parts.append(f"p.{q(ctx['pavillon_name'])} = %s")
        params.append(pavillon_filter)

    if class_filter != "Société de classification" and "c." in " ".join(joins) and ctx.get("classification_name"):
        where_parts.append(f"c.{q(ctx['classification_name'])} = %s")
        params.append(class_filter)

    sql = f"""
        SELECT
            {", ".join(select_parts)}
        FROM {q(n)} n
        {" ".join(joins)}
    """

    if where_parts:
        sql += " WHERE " + " AND ".join(where_parts)

    if year_col:
        sql += f" ORDER BY n.{q(year_col)} ASC NULLS LAST"
    elif name_col:
        sql += f" ORDER BY n.{q(name_col)} ASC NULLS LAST"

    sql += " LIMIT 50"

    return sql, params


def get_distinct_values(ctx, table_key, column_key, placeholder):
    """Valeurs distinctes pour les menus déroulants."""
    table = ctx.get(table_key)
    column = ctx.get(column_key)
    if not table or not column:
        return [placeholder]

    sql = f"""
        SELECT DISTINCT {q(column)} AS value
        FROM {q(table)}
        WHERE {q(column)} IS NOT NULL
        ORDER BY {q(column)};
    """
    try:
        values = run_query(sql)["value"].dropna().astype(str).tolist()
        return [placeholder] + values
    except Exception:
        return [placeholder]


def format_table_html(df):
    """Transforme le DataFrame en tableau HTML stylé."""
    if df.empty:
        return "<p class='small-muted'>Aucun résultat trouvé.</p>"

    html = """
    <table class="result-table">
        <thead>
            <tr>
                <th>IMO</th>
                <th>Nom du navire</th>
                <th>Type</th>
                <th>Année</th>
                <th>Pavillon</th>
                <th>GT</th>
                <th>DWT</th>
                <th>Longueur</th>
                <th>Classification</th>
                <th>Propriétaire</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in df.iterrows():
        imo = "" if pd.isna(row.get("imo")) else row.get("imo")
        name = "" if pd.isna(row.get("nom_navire")) else row.get("nom_navire")
        vessel_type = "" if pd.isna(row.get("type_navire")) else row.get("type_navire")
        year = "" if pd.isna(row.get("annee_construction")) else row.get("annee_construction")
        pavillon = "" if pd.isna(row.get("pavillon")) else row.get("pavillon")
        gt = "" if pd.isna(row.get("gt")) else row.get("gt")
        dwt = "" if pd.isna(row.get("dwt")) else row.get("dwt")
        length = "" if pd.isna(row.get("longueur")) else row.get("longueur")
        classification = "" if pd.isna(row.get("classification")) else row.get("classification")
        owner = "" if pd.isna(row.get("proprietaire")) else row.get("proprietaire")

        try:
            year_int = int(float(year))
            year_html = f"<span class='badge-year-old'>{year_int}</span>" if year_int < 1995 else f"<span class='badge-year'>{year_int}</span>"
        except Exception:
            year_html = ""

        try:
            length_html = f"{float(length):g} m" if length != "" else ""
        except Exception:
            length_html = str(length)

        html += f"""
            <tr>
                <td>{imo}</td>
                <td>{name}</td>
                <td><span class="badge-type">{vessel_type}</span></td>
                <td>{year_html}</td>
                <td>{pavillon}</td>
                <td>{gt}</td>
                <td>{dwt}</td>
                <td>{length_html}</td>
                <td>{classification}</td>
                <td>{owner}</td>
            </tr>
        """

    html += """
        </tbody>
    </table>
    """

    return html


def safe_count_table(table_name):
    if not table_name:
        return 0
    try:
        return int(run_query(f"SELECT COUNT(*) AS n FROM {q(table_name)}")["n"].iloc[0])
    except Exception:
        return 0


def safe_count_distinct(table_name, column_name):
    if not table_name or not column_name:
        return 0
    try:
        return int(run_query(f"SELECT COUNT(DISTINCT {q(column_name)}) AS n FROM {q(table_name)}")["n"].iloc[0])
    except Exception:
        return 0


# ------------------------------------------------------------
# Requêtes SQL prédéfinies
# ------------------------------------------------------------

def predefined_queries(ctx):
    n = ctx.get("navire")
    if not n:
        return {}

    # Requête 1 : navires anciens, construite selon les vraies colonnes trouvées.
    main_sql, _ = build_main_query(ctx)
    old_sql = main_sql.replace("LIMIT 50", "")
    if ctx.get("annee"):
        old_sql = old_sql.replace(f"ORDER BY n.{q(ctx['annee'])} ASC NULLS LAST", "")
        old_sql += f" WHERE n.{q(ctx['annee'])} < 1995" if " WHERE " not in old_sql else f" AND n.{q(ctx['annee'])} < 1995"
        old_sql += f" ORDER BY n.{q(ctx['annee'])} ASC NULLS LAST LIMIT 30"

    queries = {
        "1. Afficher les navires les plus anciens": old_sql.strip(),
    }

    if ctx.get("type") and ctx.get("type_name") and ctx.get("id_type") and ctx.get("type_id") and ctx.get("gt"):
        queries["2. Comparer le tonnage moyen par type de navire"] = f"""
SELECT
    t.{q(ctx['type_name'])} AS type_navire,
    ROUND(AVG(n.{q(ctx['gt'])})::numeric, 2) AS tonnage_moyen,
    COUNT(*) AS nombre_navires
FROM {q(n)} n
JOIN {q(ctx['type'])} t ON n.{q(ctx['id_type'])} = t.{q(ctx['type_id'])}
GROUP BY t.{q(ctx['type_name'])}
ORDER BY tonnage_moyen DESC;
""".strip()

    if ctx.get("pavillon") and ctx.get("pavillon_name") and ctx.get("id_pavillon") and ctx.get("pavillon_id"):
        queries["3. Trouver les pavillons les plus représentés"] = f"""
SELECT
    p.{q(ctx['pavillon_name'])} AS pavillon,
    COUNT(*) AS nombre_navires
FROM {q(n)} n
JOIN {q(ctx['pavillon'])} p ON n.{q(ctx['id_pavillon'])} = p.{q(ctx['pavillon_id'])}
GROUP BY p.{q(ctx['pavillon_name'])}
ORDER BY nombre_navires DESC;
""".strip()

    if ctx.get("proprietaire") and ctx.get("proprietaire_name") and ctx.get("id_proprietaire") and ctx.get("proprietaire_id"):
        queries["4. Lister les propriétaires possédant plusieurs navires"] = f"""
SELECT
    pr.{q(ctx['proprietaire_name'])} AS proprietaire,
    COUNT(*) AS nombre_navires
FROM {q(n)} n
JOIN {q(ctx['proprietaire'])} pr ON n.{q(ctx['id_proprietaire'])} = pr.{q(ctx['proprietaire_id'])}
GROUP BY pr.{q(ctx['proprietaire_name'])}
HAVING COUNT(*) > 1
ORDER BY nombre_navires DESC;
""".strip()

    if ctx.get("constructeur") and ctx.get("constructeur_name") and ctx.get("id_constructeur") and ctx.get("constructeur_id"):
        queries["5. Identifier les constructeurs les plus fréquents"] = f"""
SELECT
    co.{q(ctx['constructeur_name'])} AS constructeur,
    COUNT(*) AS nombre_navires
FROM {q(n)} n
JOIN {q(ctx['constructeur'])} co ON n.{q(ctx['id_constructeur'])} = co.{q(ctx['constructeur_id'])}
GROUP BY co.{q(ctx['constructeur_name'])}
ORDER BY nombre_navires DESC;
""".strip()

    if ctx.get("classification") and ctx.get("classification_name") and ctx.get("id_classification") and ctx.get("classification_id"):
        queries["6. Rechercher les navires classés par Bureau Veritas"] = f"""
SELECT
    n.{q(ctx.get('imo'))} AS imo,
    n.{q(ctx.get('nom_navire'))} AS nom_navire,
    c.{q(ctx['classification_name'])} AS classification
FROM {q(n)} n
JOIN {q(ctx['classification'])} c ON n.{q(ctx['id_classification'])} = c.{q(ctx['classification_id'])}
WHERE c.{q(ctx['classification_name'])} ILIKE '%Bureau Veritas%'
ORDER BY n.{q(ctx.get('nom_navire'))};
""".strip()

    if ctx.get("pavillon") and ctx.get("pavillon_name") and ctx.get("annee"):
        queries["7. Calculer l'âge moyen des navires par pavillon"] = f"""
SELECT
    p.{q(ctx['pavillon_name'])} AS pavillon,
    ROUND(AVG(EXTRACT(YEAR FROM CURRENT_DATE) - n.{q(ctx['annee'])})::numeric, 2) AS age_moyen
FROM {q(n)} n
JOIN {q(ctx['pavillon'])} p ON n.{q(ctx['id_pavillon'])} = p.{q(ctx['pavillon_id'])}
WHERE n.{q(ctx['annee'])} IS NOT NULL
GROUP BY p.{q(ctx['pavillon_name'])}
ORDER BY age_moyen DESC;
""".strip()

    if ctx.get("dwt"):
        queries["8. Trouver les navires avec le plus grand DWT"] = f"""
SELECT
    n.{q(ctx.get('imo'))} AS imo,
    n.{q(ctx.get('nom_navire'))} AS nom_navire,
    n.{q(ctx['dwt'])} AS dwt
FROM {q(n)} n
ORDER BY n.{q(ctx['dwt'])} DESC NULLS LAST
LIMIT 20;
""".strip()

    if ctx.get("type") and ctx.get("type_name") and ctx.get("dwt"):
        queries["9. Comparer les types de navires selon leur capacité"] = f"""
SELECT
    t.{q(ctx['type_name'])} AS type_navire,
    ROUND(AVG(n.{q(ctx['dwt'])})::numeric, 2) AS dwt_moyen,
    MAX(n.{q(ctx['dwt'])}) AS dwt_maximal,
    COUNT(*) AS nombre_navires
FROM {q(n)} n
JOIN {q(ctx['type'])} t ON n.{q(ctx['id_type'])} = t.{q(ctx['type_id'])}
GROUP BY t.{q(ctx['type_name'])}
ORDER BY dwt_moyen DESC;
""".strip()

    return queries


# ------------------------------------------------------------
# Interface principale
# ------------------------------------------------------------

try:
    ctx = detect_context()
except Exception as error:
    st.error("Connexion impossible à la base PostgreSQL.")
    st.write("Vérifie le fichier `config.json`, le nom de la base, l'utilisateur et le mot de passe.")
    st.exception(error)
    st.stop()

# Topbar
st.markdown(
    """
    <div class="topbar">
        <div>
            <div class="brand-title">VesselRegistry</div>
            <div class="brand-subtitle">Base relationnelle des navires internationaux</div>
        </div>
        <div class="nav-links">
            <span>Accueil</span>
            <span>Navires</span>
            <span>Ports</span>
            <span>Requêtes SQL</span>
            <span>Statistiques</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-title">Tableau de bord maritime</div>
    <div class="hero-subtitle">
        Interface de consultation des navires, pavillons, constructeurs, propriétaires, gestionnaires et sociétés de classification.
    </div>
    """,
    unsafe_allow_html=True
)

# Métriques
navire_count = safe_count_table(ctx.get("navire"))
pavillon_count = safe_count_table(ctx.get("pavillon"))
port_count = safe_count_table(ctx.get("port"))
classification_count = safe_count_table(ctx.get("classification"))

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Navires enregistrés</div>
        <div class="metric-value">{navire_count:,}</div>
        <div class="metric-note">données IMO</div>
    </div>
    """.replace(",", " "), unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Pavillons représentés</div>
        <div class="metric-value">{pavillon_count:,}</div>
        <div class="metric-note">pays différents</div>
    </div>
    """.replace(",", " "), unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Ports suivis</div>
        <div class="metric-value">{port_count:,}</div>
        <div class="metric-note">escales possibles</div>
    </div>
    """.replace(",", " "), unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Sociétés de classification</div>
        <div class="metric-value">{classification_count:,}</div>
        <div class="metric-note">BV, DNV, NK, KR...</div>
    </div>
    """.replace(",", " "), unsafe_allow_html=True)


# Recherche multicritère
st.markdown('<div class="panel"><div class="panel-title">Recherche multicritère</div>', unsafe_allow_html=True)

type_values = get_distinct_values(ctx, "type", "type_name", "Type de navire")
pavillon_values = get_distinct_values(ctx, "pavillon", "pavillon_name", "Pavillon")
classification_values = get_distinct_values(ctx, "classification", "classification_name", "Société de classification")

c1, c2, c3, c4 = st.columns([2.1, 1, 1, 1])
with c1:
    search_text = st.text_input("Recherche", placeholder="Rechercher par nom ou numéro IMO...", label_visibility="collapsed")
with c2:
    selected_type = st.selectbox("Type de navire", type_values, label_visibility="collapsed")
with c3:
    selected_pavillon = st.selectbox("Pavillon", pavillon_values, label_visibility="collapsed")
with c4:
    selected_classification = st.selectbox("Société de classification", classification_values, label_visibility="collapsed")

b1, b2, b3, spacer = st.columns([1.1, 0.8, 1.1, 5])
with b1:
    launch = st.button("Lancer la recherche")
with b2:
    reset = st.button("Réinitialiser")
with b3:
    export_placeholder = st.empty()

if reset:
    st.rerun()

sql, params = build_main_query(ctx, search_text, selected_type, selected_pavillon, selected_classification)
try:
    results = run_query(sql, params)
except Exception as error:
    st.error("Impossible d'exécuter la requête de recherche.")
    st.exception(error)
    results = pd.DataFrame()

if not results.empty:
    csv_data = results.to_csv(index=False).encode("utf-8")
    export_placeholder.download_button(
        label="Exporter les résultats",
        data=csv_data,
        file_name="shipdata_resultats.csv",
        mime="text/csv"
    )
else:
    export_placeholder.button("Exporter les résultats", disabled=True)

st.markdown('</div>', unsafe_allow_html=True)


# Résultats
st.markdown('<div class="panel"><div class="panel-title">Résultats de recherche</div>', unsafe_allow_html=True)
st.markdown(format_table_html(results), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# Statistiques simples
st.markdown('<div class="panel"><div class="panel-title">Statistiques rapides</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Répartition des navires par type**")
    if ctx.get("type") and ctx.get("type_name") and ctx.get("id_type") and ctx.get("type_id"):
        chart_sql = f"""
            SELECT t.{q(ctx['type_name'])} AS type_navire, COUNT(*) AS nombre_navires
            FROM {q(ctx['navire'])} n
            JOIN {q(ctx['type'])} t ON n.{q(ctx['id_type'])} = t.{q(ctx['type_id'])}
            GROUP BY t.{q(ctx['type_name'])}
            ORDER BY nombre_navires DESC
            LIMIT 10;
        """
        try:
            chart_df = run_query(chart_sql)
            st.bar_chart(chart_df.set_index("type_navire"))
        except Exception:
            st.info("Graphique indisponible avec les colonnes actuelles.")

with chart_col2:
    st.markdown("**Top pavillons**")
    if ctx.get("pavillon") and ctx.get("pavillon_name") and ctx.get("id_pavillon") and ctx.get("pavillon_id"):
        chart_sql = f"""
            SELECT p.{q(ctx['pavillon_name'])} AS pavillon, COUNT(*) AS nombre_navires
            FROM {q(ctx['navire'])} n
            JOIN {q(ctx['pavillon'])} p ON n.{q(ctx['id_pavillon'])} = p.{q(ctx['pavillon_id'])}
            GROUP BY p.{q(ctx['pavillon_name'])}
            ORDER BY nombre_navires DESC
            LIMIT 10;
        """
        try:
            chart_df = run_query(chart_sql)
            st.bar_chart(chart_df.set_index("pavillon"))
        except Exception:
            st.info("Graphique indisponible avec les colonnes actuelles.")

st.markdown('</div>', unsafe_allow_html=True)


# Requêtes SQL disponibles
queries = predefined_queries(ctx)
query_titles = list(queries.keys())

st.markdown('<div class="section-separator"></div>', unsafe_allow_html=True)
left, right = st.columns([1.05, 1])

with left:
    st.markdown('<div class="panel"><div class="panel-title">Requêtes SQL disponibles</div>', unsafe_allow_html=True)

    if "selected_query" not in st.session_state:
        st.session_state.selected_query = query_titles[0] if query_titles else None

    for title in query_titles:
        if st.button(title, key=f"query_{title}", use_container_width=True):
            st.session_state.selected_query = title

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel"><div class="panel-title">Aperçu SQL</div>', unsafe_allow_html=True)

    selected_sql = queries.get(st.session_state.get("selected_query"), "")
    st.markdown(f'<div class="sql-box">{selected_sql}</div>', unsafe_allow_html=True)

    if selected_sql:
        if st.button("Exécuter cette requête", use_container_width=True):
            try:
                query_result = run_query(selected_sql)
                st.dataframe(query_result, use_container_width=True)
            except Exception as error:
                st.error("Impossible d'exécuter cette requête.")
                st.exception(error)

    st.markdown('</div>', unsafe_allow_html=True)


# Structure de la base
with st.expander("Voir la structure détectée de la base"):
    st.write("Tables trouvées :", get_tables())
    st.json({k: v for k, v in ctx.items() if v is not None})

st.markdown(
    """
    <div style="text-align:center;color:#94a3b8;font-size:0.85rem;margin-top:2.5rem;">
        Projet de bases de données — ShipData / VesselRegistry — Interface prototype Streamlit
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)
