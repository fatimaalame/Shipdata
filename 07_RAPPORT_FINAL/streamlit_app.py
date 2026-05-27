from pathlib import Path
import json
import unicodedata

import altair as alt
import pandas as pd
import psycopg2
import streamlit as st


# ============================================================
# ShipData - Interface Streamlit avec rôles utilisateur
# ============================================================
# Lancement conseillé depuis la racine du projet :
# python -m streamlit run .\07_RAPPORT_FINAL\streamlit_app.py
#
# Comptes de démonstration :
# - client / client123
# - capitaine / capitaine123
# - employe / employe123
# - admin / admin123
# ============================================================


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

# Le fichier streamlit_app.py est dans 07_RAPPORT_FINAL.
# parents[1] remonte à la racine du projet.
ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "config.json"


# ------------------------------------------------------------
# Comptes de démonstration et rôles
# ------------------------------------------------------------

USERS = {
    "client": {
        "password": "client123",
        "role": "client",
        "label": "Client",
    },
    "capitaine": {
        "password": "capitaine123",
        "role": "employe_capitaine",
        "label": "Employé / capitaine",
    },
    "employe": {
        "password": "employe123",
        "role": "employe_capitaine",
        "label": "Employé / capitaine",
    },
    "admin": {
        "password": "admin123",
        "role": "administrateur",
        "label": "Administrateur",
    },
}

ROLE_LABELS = {
    "client": "Client",
    "employe_capitaine": "Employé / capitaine",
    "administrateur": "Administrateur",
}


# ------------------------------------------------------------
# CSS
# ------------------------------------------------------------

st.markdown(
    """
    <style>
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
        --page-x: clamp(2.5rem, 5vw, 5.5rem);

        padding-top: 0rem !important;
        padding-left: var(--page-x) !important;
        padding-right: var(--page-x) !important;
        padding-bottom: 3rem !important;
        max-width: 100% !important;
    }

    .main-content {
        padding: 2.4rem 0 3.2rem 0;
    }

    .topbar {
        background: var(--navy);
        color: white;
        margin-left: calc(0px - var(--page-x));
        margin-right: calc(0px - var(--page-x));
        padding: 1.25rem var(--page-x);
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

    .role-pill {
        display: inline-block;
        background: rgba(14, 165, 233, 0.15);
        color: #e0f2fe;
        border: 1px solid rgba(224, 242, 254, 0.22);
        border-radius: 999px;
        padding: 0.45rem 0.85rem;
        font-weight: 800;
        font-size: 0.86rem;
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

    .login-card {
        background: white;
        border-radius: 18px;
        padding: 2rem;
        max-width: 520px;
        margin: 7vh auto 0 auto;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.10);
        border: 1px solid rgba(229, 231, 235, 0.85);
    }

    .login-title {
        font-size: 2rem;
        font-weight: 850;
        color: #111827;
        margin-bottom: 0.3rem;
    }

    .login-subtitle {
        color: #6b7280;
        margin-bottom: 1.4rem;
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

    .panel-help {
        color: #6b7280;
        font-size: 0.92rem;
        margin-top: -0.45rem;
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
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextArea"] > div {
        border-radius: 10px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    .section-separator {
        height: 1rem;
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Authentification
# ------------------------------------------------------------

def is_logged_in():
    """Vérifie si l'utilisateur est connecté."""
    return st.session_state.get("authenticated", False)


def get_current_role():
    """Renvoie le rôle courant."""
    return st.session_state.get("role", "client")


def get_current_role_label():
    """Renvoie le libellé du rôle courant."""
    return st.session_state.get(
        "role_label",
        ROLE_LABELS.get(get_current_role(), "Utilisateur")
    )


def can_view_sql():
    """Les clients ne voient pas les requêtes SQL avancées."""
    return get_current_role() in ["employe_capitaine", "administrateur"]


def can_export_results():
    """Les employés/capitaines et administrateurs peuvent exporter."""
    return get_current_role() in ["employe_capitaine", "administrateur"]


def is_admin():
    """Vérifie si l'utilisateur est administrateur."""
    return get_current_role() == "administrateur"


def logout():
    """Déconnecte l'utilisateur."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.role_label = None
    st.rerun()


def login_screen():
    """Affiche l'écran de connexion."""
    st.markdown(
        """
        <div class="login-card">
            <div class="login-title">ShipDATA</div>
            <div class="login-subtitle">
                Connecte-toi pour accéder à l'interface adaptée à ton rôle.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("Se connecter", use_container_width=True)

    with st.expander("Comptes de démonstration"):
        st.write("Client : `client` / `client123`")
        st.write("Employé / capitaine : `capitaine` / `capitaine123`")
        st.write("Employé : `employe` / `employe123`")
        st.write("Administrateur : `admin` / `admin123`")

    if submit:
        user = USERS.get(username.strip().lower())

        if user and password == user["password"]:
            st.session_state.authenticated = True
            st.session_state.username = username.strip().lower()
            st.session_state.role = user["role"]
            st.session_state.role_label = user["label"]
            st.rerun()

        st.error("Nom d'utilisateur ou mot de passe incorrect.")


# ------------------------------------------------------------
# Fonctions utilitaires
# ------------------------------------------------------------

def normalize(text):
    """Simplifie un texte pour comparer les noms de tables/colonnes."""
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
    normalized = {normalize(table): table for table in tables}

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
    normalized = {normalize(column): column for column in columns}

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
    propriete_navire_table = find_table(["propriete_navire", "propriete navire", "ownership", "navire_proprietaire"])
    constructeur_table = find_table(["constructeur", "builder"])
    port_table = find_table(["port", "ports"])
    escale_table = find_table(["escale", "escales"])

    ctx = {
        "navire": navire_table,
        "type": type_table,
        "pavillon": pavillon_table,
        "classification": classification_table,
        "proprietaire": proprietaire_table,
        "propriete_navire": propriete_navire_table,
        "constructeur": constructeur_table,
        "port": port_table,
        "escale": escale_table,
    }

    if navire_table:
        ctx.update({
            "imo": find_column(navire_table, ["imo", "numero_imo", "imo_number", "num_imo"]),
            "mmsi": find_column(navire_table, ["mmsi"]),
            "nom_navire": find_column(navire_table, ["nom_navire", "nom", "name", "vessel_name"]),
            "annee": find_column(navire_table, ["annee_construction", "annee", "year_built", "construction_year"]),
            "gt": find_column(navire_table, ["gt", "gross_tonnage", "tonnage_brut"]),
            "dwt": find_column(navire_table, ["dwt", "deadweight", "deadweight_tonnage"]),
            "longueur": find_column(navire_table, ["longueur", "longueur_m", "length", "loa"]),
            "largeur": find_column(navire_table, ["largeur", "largeur_m", "width"]),
            "tirant_eau": find_column(navire_table, ["tirant_eau", "tirant_eau_m", "draft"]),
            "id_type": find_column(navire_table, ["id_type", "id_type_navire", "type_id"]),
            "id_pavillon": find_column(navire_table, ["id_pavillon", "pavillon_id", "id_flag"]),
            "id_classification": find_column(navire_table, ["id_classification", "id_societe_classification", "classification_id"]),
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
            "classification_sigle": find_column(classification_table, ["sigle", "code", "abbreviation"]),
        })

    if proprietaire_table:
        ctx.update({
            "proprietaire_id": find_column(proprietaire_table, ["id_proprietaire", "id"]),
            "proprietaire_name": find_column(proprietaire_table, ["nom_proprietaire", "proprietaire", "owner", "nom"]),
        })

    if propriete_navire_table:
        ctx.update({
            "ownership_imo": find_column(propriete_navire_table, ["imo", "id_navire"]),
            "ownership_proprietaire_id": find_column(propriete_navire_table, ["id_proprietaire", "proprietaire_id", "owner_id"]),
            "ownership_date_fin": find_column(propriete_navire_table, ["date_fin", "end_date"]),
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
            "port_country": find_column(port_table, ["code_iso2_pays", "pays", "country", "nom_pays"]),
            "port_size": find_column(port_table, ["taille_port", "taille", "size"]),
        })

    return ctx


# ------------------------------------------------------------
# Construction SQL
# ------------------------------------------------------------

def build_main_query(
    ctx,
    search_text="",
    type_filter="Type de navire",
    pavillon_filter="Pavillon",
    class_filter="Société de classification"
):
    """Construit la requête principale de recherche."""
    n = ctx["navire"]

    if not n:
        return None, []

    select_parts = []
    joins = []
    where_parts = []
    params = []

    imo_col = ctx.get("imo")
    mmsi_col = ctx.get("mmsi")
    name_col = ctx.get("nom_navire")
    year_col = ctx.get("annee")
    gt_col = ctx.get("gt")
    dwt_col = ctx.get("dwt")
    length_col = ctx.get("longueur")
    width_col = ctx.get("largeur")
    draft_col = ctx.get("tirant_eau")

    select_parts.append(f"n.{q(imo_col)} AS imo" if imo_col else "NULL AS imo")
    select_parts.append(f"n.{q(mmsi_col)} AS mmsi" if mmsi_col else "NULL AS mmsi")
    select_parts.append(f"n.{q(name_col)} AS nom_navire" if name_col else "NULL AS nom_navire")

    if ctx.get("type") and ctx.get("id_type") and ctx.get("type_id") and ctx.get("type_name"):
        joins.append(
            f"LEFT JOIN {q(ctx['type'])} t "
            f"ON n.{q(ctx['id_type'])} = t.{q(ctx['type_id'])}"
        )
        select_parts.append(f"t.{q(ctx['type_name'])} AS type_navire")
    else:
        select_parts.append("NULL AS type_navire")

    select_parts.append(f"n.{q(year_col)} AS annee_construction" if year_col else "NULL AS annee_construction")

    if ctx.get("pavillon") and ctx.get("id_pavillon") and ctx.get("pavillon_id") and ctx.get("pavillon_name"):
        joins.append(
            f"LEFT JOIN {q(ctx['pavillon'])} p "
            f"ON n.{q(ctx['id_pavillon'])} = p.{q(ctx['pavillon_id'])}"
        )
        select_parts.append(f"p.{q(ctx['pavillon_name'])} AS pavillon")
    else:
        select_parts.append("NULL AS pavillon")

    select_parts.append(f"n.{q(gt_col)} AS gt" if gt_col else "NULL AS gt")
    select_parts.append(f"n.{q(dwt_col)} AS dwt" if dwt_col else "NULL AS dwt")
    select_parts.append(f"n.{q(length_col)} AS longueur" if length_col else "NULL AS longueur")
    select_parts.append(f"n.{q(width_col)} AS largeur" if width_col else "NULL AS largeur")
    select_parts.append(f"n.{q(draft_col)} AS tirant_eau" if draft_col else "NULL AS tirant_eau")

    if (
        ctx.get("classification")
        and ctx.get("id_classification")
        and ctx.get("classification_id")
        and ctx.get("classification_name")
    ):
        joins.append(
            f"LEFT JOIN {q(ctx['classification'])} c "
            f"ON n.{q(ctx['id_classification'])} = c.{q(ctx['classification_id'])}"
        )
        select_parts.append(f"c.{q(ctx['classification_name'])} AS classification")
    else:
        select_parts.append("NULL AS classification")

    if (
        ctx.get("constructeur")
        and ctx.get("id_constructeur")
        and ctx.get("constructeur_id")
        and ctx.get("constructeur_name")
    ):
        joins.append(
            f"LEFT JOIN {q(ctx['constructeur'])} co "
            f"ON n.{q(ctx['id_constructeur'])} = co.{q(ctx['constructeur_id'])}"
        )
        select_parts.append(f"co.{q(ctx['constructeur_name'])} AS constructeur")
    else:
        select_parts.append("NULL AS constructeur")

    if (
        ctx.get("propriete_navire")
        and ctx.get("proprietaire")
        and ctx.get("ownership_imo")
        and ctx.get("ownership_proprietaire_id")
        and ctx.get("proprietaire_id")
        and ctx.get("proprietaire_name")
    ):
        ownership_join = (
            f"LEFT JOIN {q(ctx['propriete_navire'])} pn "
            f"ON n.{q(imo_col)} = pn.{q(ctx['ownership_imo'])}"
        )

        if ctx.get("ownership_date_fin"):
            ownership_join += f" AND pn.{q(ctx['ownership_date_fin'])} IS NULL"

        joins.append(ownership_join)
        joins.append(
            f"LEFT JOIN {q(ctx['proprietaire'])} pr "
            f"ON pn.{q(ctx['ownership_proprietaire_id'])} = pr.{q(ctx['proprietaire_id'])}"
        )
        select_parts.append(f"pr.{q(ctx['proprietaire_name'])} AS proprietaire")
    else:
        select_parts.append("NULL AS proprietaire")

    if search_text.strip():
        search_value = f"%{search_text.strip()}%"
        text_conditions = []

        if name_col:
            text_conditions.append(f"CAST(n.{q(name_col)} AS TEXT) ILIKE %s")
            params.append(search_value)

        if imo_col:
            text_conditions.append(f"CAST(n.{q(imo_col)} AS TEXT) ILIKE %s")
            params.append(search_value)

        if mmsi_col:
            text_conditions.append(f"CAST(n.{q(mmsi_col)} AS TEXT) ILIKE %s")
            params.append(search_value)

        if text_conditions:
            where_parts.append("(" + " OR ".join(text_conditions) + ")")

    if type_filter != "Type de navire" and ctx.get("type_name"):
        where_parts.append(f"t.{q(ctx['type_name'])} = %s")
        params.append(type_filter)

    if pavillon_filter != "Pavillon" and ctx.get("pavillon_name"):
        where_parts.append(f"p.{q(ctx['pavillon_name'])} = %s")
        params.append(pavillon_filter)

    if class_filter != "Société de classification" and ctx.get("classification_name"):
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


# ------------------------------------------------------------
# Préparation de l'affichage
# ------------------------------------------------------------

def format_meter_value(value):
    """Ajoute l'unité m aux valeurs de dimensions."""
    if pd.isna(value) or value == "":
        return ""

    try:
        return f"{float(value):g} m"
    except Exception:
        return str(value)


def prepare_display_dataframe(df):
    """Prépare le tableau selon le rôle connecté."""
    if df.empty:
        return df

    role = get_current_role()
    display_df = df.copy()

    rename_map = {
        "imo": "IMO",
        "mmsi": "MMSI",
        "nom_navire": "Nom du navire",
        "type_navire": "Type",
        "annee_construction": "Année",
        "pavillon": "Pavillon",
        "gt": "GT",
        "dwt": "DWT",
        "longueur": "Longueur",
        "largeur": "Largeur",
        "tirant_eau": "Tirant d'eau",
        "classification": "Classification",
        "constructeur": "Constructeur",
        "proprietaire": "Propriétaire actuel",
    }

    display_df = display_df.rename(columns=rename_map)

    if role == "client":
        wanted_columns = [
            "IMO",
            "Nom du navire",
            "Type",
            "Année",
            "Pavillon",
            "Longueur",
        ]
    elif role == "employe_capitaine":
        wanted_columns = [
            "IMO",
            "MMSI",
            "Nom du navire",
            "Type",
            "Année",
            "Pavillon",
            "GT",
            "DWT",
            "Longueur",
            "Classification",
            "Propriétaire actuel",
        ]
    else:
        wanted_columns = [
            "IMO",
            "MMSI",
            "Nom du navire",
            "Type",
            "Année",
            "Pavillon",
            "GT",
            "DWT",
            "Longueur",
            "Largeur",
            "Tirant d'eau",
            "Classification",
            "Constructeur",
            "Propriétaire actuel",
        ]

    existing_columns = [column for column in wanted_columns if column in display_df.columns]
    display_df = display_df[existing_columns]

    for col in ["Longueur", "Largeur", "Tirant d'eau"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(format_meter_value)

    return display_df


def style_display_dataframe(display_df):
    """Ajoute un style léger au tableau Streamlit."""
    if display_df.empty:
        return display_df

    def highlight_old_year(value):
        try:
            year = int(float(value))
            if year < 1995:
                return "background-color: #ffe4ec; color: #be123c; font-weight: 700;"
        except Exception:
            pass

        return ""

    styler = display_df.style

    if "Année" in display_df.columns:
        styler = styler.map(highlight_old_year, subset=["Année"])

    return styler


def safe_count_table(table_name):
    """Compte les lignes d'une table."""
    if not table_name:
        return 0

    try:
        return int(run_query(f"SELECT COUNT(*) AS n FROM {q(table_name)}")["n"].iloc[0])
    except Exception:
        return 0


def show_bar_chart_with_margins(df, x_col, y_col, height=360):
    """Affiche un graphique en barres avec des marges internes contrôlées."""
    if df.empty:
        st.info("Aucune donnée disponible pour ce graphique.")
        return

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(
                f"{x_col}:N",
                sort="-y",
                title=None,
                axis=alt.Axis(
                    labelAngle=-90,
                    labelPadding=8,
                    labelLimit=160
                )
            ),
            y=alt.Y(
                f"{y_col}:Q",
                title=None,
                axis=alt.Axis(
                    labelPadding=10
                )
            ),
            tooltip=[
                alt.Tooltip(f"{x_col}:N", title=x_col),
                alt.Tooltip(f"{y_col}:Q", title=y_col),
            ],
        )
        .properties(
            height=height,
            padding={
                "left": 35,
                "right": 15,
                "top": 15,
                "bottom": 70
            }
        )
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(chart, use_container_width=True)


# ------------------------------------------------------------
# Requêtes SQL officielles du projet
# ------------------------------------------------------------

def predefined_queries():
    """Requêtes SQL visibles pour les rôles employés/capitaines et administrateurs."""
    return {
        "R00 - Navires construits avant 1995": """
SELECT imo, nom_navire, annee_construction
FROM navire
WHERE annee_construction < 1995
ORDER BY annee_construction;
""".strip(),

        "R01 - Navires avec type, catégorie et pavillon": """
SELECT
    n.imo,
    n.nom_navire,
    t.nom_type AS type_navire,
    c.nom_categorie AS categorie,
    p.nom_pays AS pavillon
FROM navire n
JOIN type_navire t ON n.id_type_navire = t.id_type_navire
JOIN categorie_principale c ON t.id_categorie = c.id_categorie
JOIN pavillon p ON n.id_pavillon = p.id_pavillon
ORDER BY c.nom_categorie, t.nom_type, n.nom_navire;
""".strip(),

        "R02 - Nombre de navires par catégorie": """
SELECT
    c.nom_categorie,
    COUNT(n.imo) AS nb_navires
FROM categorie_principale c
JOIN type_navire t ON t.id_categorie = c.id_categorie
JOIN navire n ON n.id_type_navire = t.id_type_navire
GROUP BY c.id_categorie, c.nom_categorie
ORDER BY nb_navires DESC;
""".strip(),

        "R03 - Top 5 ports avec le plus d'escales": """
SELECT
    p.nom_port,
    p.code_iso2_pays AS pays,
    p.taille_port,
    COUNT(e.id_escale) AS nb_escales
FROM port p
JOIN escale e ON e.id_port = p.id_port
GROUP BY p.id_port, p.nom_port, p.code_iso2_pays, p.taille_port
ORDER BY nb_escales DESC
LIMIT 5;
""".strip(),

        "R04 - Historique des propriétaires de CHS ALPHA": """
SELECT
    n.nom_navire,
    pr.nom_proprietaire,
    pn.date_debut,
    pn.date_fin,
    CASE
        WHEN pn.date_fin IS NULL THEN 'Propriétaire actuel'
        ELSE 'Ancien propriétaire'
    END AS statut
FROM propriete_navire pn
JOIN navire n ON pn.imo = n.imo
JOIN proprietaire pr ON pn.id_proprietaire = pr.id_proprietaire
WHERE n.imo = (SELECT imo FROM navire WHERE nom_navire = 'CHS ALPHA')
ORDER BY pn.date_debut;
""".strip(),

        "R05 - Navires ayant plusieurs propriétaires": """
SELECT
    n.nom_navire,
    COUNT(pn.id_proprietaire) AS nb_proprietaires
FROM navire n
JOIN propriete_navire pn ON pn.imo = n.imo
GROUP BY n.imo, n.nom_navire
HAVING COUNT(pn.id_proprietaire) > 1
ORDER BY nb_proprietaires DESC;
""".strip(),

        "R06 - Tonnage moyen par pavillon": """
SELECT
    p.nom_pays AS pavillon,
    COUNT(n.imo) AS nb_navires,
    ROUND(AVG(n.gross_tonnage)) AS gross_tonnage_moyen,
    ROUND(AVG(n.deadweight_tonnage)) AS port_en_lourd_moyen
FROM pavillon p
JOIN navire n ON n.id_pavillon = p.id_pavillon
GROUP BY p.id_pavillon, p.nom_pays
ORDER BY nb_navires DESC, gross_tonnage_moyen DESC;
""".strip(),

        "R07 - Navires classés par DNV": """
SELECT
    n.nom_navire,
    n.annee_construction,
    n.gross_tonnage,
    n.deadweight_tonnage,
    s.sigle AS societe_classification
FROM navire n
JOIN societe_classification s
    ON n.id_societe_classification = s.id_societe_classification
WHERE s.sigle = 'DNV'
ORDER BY n.gross_tonnage DESC;
""".strip(),

        "R08 - Âge moyen des navires par type": """
SELECT
    t.nom_type,
    ROUND(AVG(2026 - n.annee_construction), 1) AS age_moyen
FROM navire n
JOIN type_navire t ON n.id_type_navire = t.id_type_navire
GROUP BY t.nom_type
ORDER BY age_moyen DESC;
""".strip(),

        "R09 - Classement des navires par tonnage dans chaque catégorie": """
SELECT
    c.nom_categorie,
    n.nom_navire,
    n.gross_tonnage,
    RANK() OVER (
        PARTITION BY c.id_categorie
        ORDER BY n.gross_tonnage DESC
    ) AS rang_dans_categorie
FROM navire n
JOIN type_navire t ON n.id_type_navire = t.id_type_navire
JOIN categorie_principale c ON t.id_categorie = c.id_categorie
ORDER BY c.nom_categorie, rang_dans_categorie;
""".strip(),

        "R10 - Escales du navire NIVIN": """
SELECT
    po.nom_port,
    po.code_iso2_pays AS pays,
    e.date_arrivee,
    e.date_depart
FROM escale e
JOIN navire n ON e.imo = n.imo
JOIN port po ON e.id_port = po.id_port
WHERE n.nom_navire = 'NIVIN'
ORDER BY e.date_arrivee;
""".strip(),

        "R11 - Navires passés par Savona entre le 15 et le 18 avril 2023": """
SELECT
    n.nom_navire,
    e.date_arrivee,
    e.date_depart
FROM escale e
JOIN navire n ON e.imo = n.imo
JOIN port po ON e.id_port = po.id_port
WHERE po.nom_port = 'Savona'
  AND e.date_arrivee BETWEEN '2023-04-15' AND '2023-04-18'
ORDER BY e.date_arrivee;
""".strip(),

        "R12 - Propriétaires du navire IMO 8206533": """
SELECT
    n.nom_navire,
    pr.nom_proprietaire,
    pr.code_iso2_pays,
    pr.annee_creation,
    pn.date_debut,
    pn.date_fin
FROM propriete_navire pn
JOIN navire n ON pn.imo = n.imo
JOIN proprietaire pr ON pn.id_proprietaire = pr.id_proprietaire
WHERE n.imo = 8206533
ORDER BY pn.date_debut;
""".strip(),

        "R13 - Nombre de navires par pavillon": """
SELECT
    p.nom_pays AS pavillon,
    COUNT(n.imo) AS nb_navires
FROM navire n
JOIN pavillon p ON n.id_pavillon = p.id_pavillon
GROUP BY p.nom_pays
ORDER BY nb_navires DESC;
""".strip(),
    }


def is_safe_select_query(sql):
    """Autorise seulement les requêtes SELECT/WITH pour l'espace administrateur."""
    cleaned = sql.strip().lower()

    if not cleaned:
        return False

    if not (cleaned.startswith("select") or cleaned.startswith("with")):
        return False

    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "grant",
        "revoke",
    ]

    return not any(keyword in cleaned for keyword in forbidden_keywords)


# ------------------------------------------------------------
# Écran de connexion
# ------------------------------------------------------------

if not is_logged_in():
    login_screen()
    st.stop()


# ------------------------------------------------------------
# Connexion à la base et détection du contexte
# ------------------------------------------------------------

try:
    ctx = detect_context()
except Exception as error:
    st.error("Connexion impossible à la base PostgreSQL.")
    st.write("Vérifie le fichier `config.json`, le nom de la base, l'utilisateur et le mot de passe.")
    st.exception(error)
    st.stop()


# ------------------------------------------------------------
# Interface principale
# ------------------------------------------------------------

role_label = get_current_role_label()

st.markdown(
    f"""
    <div class="topbar">
        <div>
            <div class="brand-title">ShipDATA</div>
            <div class="brand-subtitle">Interface de consultation et d'analyse maritime</div>
        </div>
        <div class="role-pill">{role_label}</div>
    </div>
    """,
    unsafe_allow_html=True
)

logout_col_1, logout_col_2 = st.columns([8, 1])
with logout_col_2:
    if st.button("Déconnexion", use_container_width=True):
        logout()

st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-title">Tableau de bord maritime</div>
    <div class="hero-subtitle">
        Interface de consultation des navires, pavillons, constructeurs, propriétaires,
        ports, escales et sociétés de classification.
    </div>
    """,
    unsafe_allow_html=True
)


# ------------------------------------------------------------
# Métriques
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Recherche multicritère
# ------------------------------------------------------------

st.markdown(
    """
    <div class="panel">
        <div class="panel-title">Recherche multicritère</div>
        <div class="panel-help">
            Les informations affichées changent selon le rôle connecté.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

type_values = get_distinct_values(ctx, "type", "type_name", "Type de navire")
pavillon_values = get_distinct_values(ctx, "pavillon", "pavillon_name", "Pavillon")
classification_values = get_distinct_values(
    ctx,
    "classification",
    "classification_name",
    "Société de classification"
)

if get_current_role() == "client":
    c1, c2, c3 = st.columns([2.2, 1, 1])

    with c1:
        search_text = st.text_input(
            "Recherche",
            placeholder="Rechercher par nom, IMO ou MMSI...",
            label_visibility="collapsed"
        )

    with c2:
        selected_type = st.selectbox(
            "Type de navire",
            type_values,
            label_visibility="collapsed"
        )

    with c3:
        selected_pavillon = st.selectbox(
            "Pavillon",
            pavillon_values,
            label_visibility="collapsed"
        )

    selected_classification = "Société de classification"

else:
    c1, c2, c3, c4 = st.columns([2.1, 1, 1, 1])

    with c1:
        search_text = st.text_input(
            "Recherche",
            placeholder="Rechercher par nom, IMO ou MMSI...",
            label_visibility="collapsed"
        )

    with c2:
        selected_type = st.selectbox(
            "Type de navire",
            type_values,
            label_visibility="collapsed"
        )

    with c3:
        selected_pavillon = st.selectbox(
            "Pavillon",
            pavillon_values,
            label_visibility="collapsed"
        )

    with c4:
        selected_classification = st.selectbox(
            "Société de classification",
            classification_values,
            label_visibility="collapsed"
        )

button_col_1, button_col_2, button_col_3, spacer = st.columns([1.1, 0.9, 1.2, 5])

with button_col_1:
    launch = st.button("Lancer la recherche")

with button_col_2:
    if st.button("Réinitialiser"):
        st.rerun()

with button_col_3:
    export_placeholder = st.empty()

sql, params = build_main_query(
    ctx,
    search_text,
    selected_type,
    selected_pavillon,
    selected_classification
)

try:
    results = run_query(sql, params)
except Exception as error:
    st.error("Impossible d'exécuter la requête de recherche.")
    st.exception(error)
    results = pd.DataFrame()

if can_export_results() and not results.empty:
    csv_data = results.to_csv(index=False).encode("utf-8")
    export_placeholder.download_button(
        label="Exporter CSV",
        data=csv_data,
        file_name="shipdata_resultats.csv",
        mime="text/csv"
    )
elif not can_export_results():
    export_placeholder.button("Export réservé", disabled=True)
else:
    export_placeholder.button("Exporter CSV", disabled=True)


# ------------------------------------------------------------
# Résultats
# ------------------------------------------------------------

st.markdown('<div class="panel"><div class="panel-title">Résultats de recherche</div>', unsafe_allow_html=True)

if results.empty:
    st.info("Aucun résultat trouvé.")
else:
    display_results = prepare_display_dataframe(results)
    st.dataframe(
        style_display_dataframe(display_results),
        use_container_width=True,
        hide_index=True,
        height=420
    )

st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# Statistiques rapides
# ------------------------------------------------------------

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
            show_bar_chart_with_margins(chart_df, "type_navire", "nombre_navires")
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
            show_bar_chart_with_margins(chart_df, "pavillon", "nombre_navires")
        except Exception:
            st.info("Graphique indisponible avec les colonnes actuelles.")

if get_current_role() in ["employe_capitaine", "administrateur"]:
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown("**Constructeurs les plus représentés**")

        chart_sql = """
            SELECT co.nom_constructeur AS constructeur, COUNT(*) AS nombre_navires
            FROM navire n
            JOIN constructeur co ON n.id_constructeur = co.id_constructeur
            GROUP BY co.nom_constructeur
            ORDER BY nombre_navires DESC
            LIMIT 10;
        """

        try:
            chart_df = run_query(chart_sql)
            show_bar_chart_with_margins(chart_df, "constructeur", "nombre_navires")
        except Exception:
            st.info("Graphique indisponible.")

    with chart_col4:
        st.markdown("**Ports avec le plus d'escales**")

        chart_sql = """
            SELECT p.nom_port AS port, COUNT(e.id_escale) AS nombre_escales
            FROM port p
            JOIN escale e ON e.id_port = p.id_port
            GROUP BY p.nom_port
            ORDER BY nombre_escales DESC
            LIMIT 10;
        """

        try:
            chart_df = run_query(chart_sql)
            show_bar_chart_with_margins(chart_df, "port", "nombre_escales")
        except Exception:
            st.info("Graphique indisponible.")

st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# Requêtes SQL prédéfinies
# ------------------------------------------------------------

if can_view_sql():
    queries = predefined_queries()
    query_titles = list(queries.keys())

    st.markdown('<div class="section-separator"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.05, 1])

    with left:
        st.markdown(
            '<div class="panel"><div class="panel-title">Requêtes SQL disponibles</div>',
            unsafe_allow_html=True
        )

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
                    st.dataframe(query_result, use_container_width=True, hide_index=True)
                except Exception as error:
                    st.error("Impossible d'exécuter cette requête.")
                    st.exception(error)

        st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# Requête personnalisée réservée à l'administrateur
# ------------------------------------------------------------

if is_admin():
    st.markdown(
        '<div class="panel"><div class="panel-title">Requête SELECT personnalisée</div>',
        unsafe_allow_html=True
    )

    custom_sql = st.text_area(
        "Écrire une requête SQL",
        placeholder="SELECT * FROM navire LIMIT 10;",
        height=130
    )

    if st.button("Exécuter la requête personnalisée"):
        if is_safe_select_query(custom_sql):
            try:
                custom_result = run_query(custom_sql)
                st.dataframe(custom_result, use_container_width=True, hide_index=True)
            except Exception as error:
                st.error("Impossible d'exécuter cette requête.")
                st.exception(error)
        else:
            st.warning("Seules les requêtes SELECT ou WITH sans modification de données sont autorisées.")

    st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# Structure de la base réservée à l'administrateur
# ------------------------------------------------------------

if is_admin():
    with st.expander("Voir la structure détectée de la base"):
        st.write("Tables trouvées :", get_tables())
        st.json({key: value for key, value in ctx.items() if value is not None})


# ------------------------------------------------------------
# Pied de page
# ------------------------------------------------------------

st.markdown(
    """
    <div style="text-align:center;color:#94a3b8;font-size:0.85rem;margin-top:2.5rem;">
        Projet de bases de données — ShipData — Interface Streamlit avec rôles utilisateur
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)