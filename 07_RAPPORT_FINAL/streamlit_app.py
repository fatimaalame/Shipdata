from datetime import date, time
from pathlib import Path
import base64
import json
import re

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
# - visiteur / visiteur123
# - employe / employe123
# - admin / admin123
# ============================================================


# ------------------------------------------------------------
# Configuration générale
# ------------------------------------------------------------

st.set_page_config(
    page_title="ShipData",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def find_project_root():
    """
    Trouve automatiquement la racine du projet.
    On cherche un dossier qui contient config.json, README.md,
    ou les dossiers importants du projet.
    """
    current_path = Path(__file__).resolve()

    for parent in [current_path.parent] + list(current_path.parents):
        has_config = (parent / "config.json").exists()
        has_readme = (parent / "README.md").exists()
        has_report_folder = (parent / "07_RAPPORT_FINAL").exists()
        has_sql_folder = (parent / "05_SQL").exists()

        if has_config or (has_readme and has_report_folder) or has_sql_folder:
            return parent

    return current_path.parent


ROOT_DIR = find_project_root()
CONFIG_PATH = ROOT_DIR / "config.json"


USERS = {
    "visiteur": {
        "password": "visiteur123",
        "role": "visiteur",
        "label": "Visiteur",
    },
    "client": {
        "password": "client123",
        "role": "visiteur",
        "label": "Visiteur",
    },
    "employe": {
        "password": "employe123",
        "role": "employe",
        "label": "Employé / capitaine",
    },
    "capitaine": {
        "password": "capitaine123",
        "role": "employe",
        "label": "Employé / capitaine",
    },
    "admin": {
        "password": "admin123",
        "role": "administrateur",
        "label": "Administrateur",
    },
}

ROLE_LABELS = {
    "visiteur": "Visiteur",
    "employe": "Employé / capitaine",
    "administrateur": "Administrateur",
}

SEARCH_DEFAULTS = {
    "search_text": "",
    "selected_type": "Type de navire",
    "selected_pavillon": "Pavillon",
    "selected_classification": "Société de classification",
}


# ------------------------------------------------------------
# Fonctions pour l'image de fond de la page d'accueil
# ------------------------------------------------------------

def image_to_base64(image_path):
    """Convertit une image locale en base64 pour l'utiliser dans le CSS."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def get_login_background_data_url():
    """
    Cherche automatiquement l'image de fond dans :
    07_RAPPORT_FINAL/INTERFACE/ProjetBD_Background.jpg, .jpeg, .png, .webp
    ou sans extension.
    """
    image_dir = Path(__file__).resolve().parent / "INTERFACE"

    candidates = [
        image_dir / "ProjetBD_Background.jpg",
        image_dir / "ProjetBD_Background.jpeg",
        image_dir / "ProjetBD_Background.png",
        image_dir / "ProjetBD_Background.webp",
        image_dir / "ProjetBD_Background",
    ]

    mime_by_suffix = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        "": "image/jpeg",
    }

    for image_path in candidates:
        if image_path.exists():
            suffix = image_path.suffix.lower()
            mime_type = mime_by_suffix.get(suffix, "image/jpeg")
            encoded_image = image_to_base64(image_path)
            return f"data:{mime_type};base64,{encoded_image}"

    return None


# ------------------------------------------------------------
# Style CSS général
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
        padding: 0.35rem 0 3.2rem 0;
        margin-top: 6.4rem;
    }

    .topbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;

        background: var(--navy);
        color: white;
        padding: 1.25rem var(--page-x);

        display: flex;
        justify-content: space-between;
        align-items: center;

        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.22);
    }

    .topbar-actions {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        flex-wrap: nowrap;
    }

    .brand-title {
        font-size: 2.1rem;
        font-weight: 900;
        margin: 0;
        line-height: 1.05;
        letter-spacing: -0.03em;
    }

    .brand-subtitle {
        color: #cbd5e1;
        font-size: 0.95rem;
        margin-top: 0.25rem;
        font-weight: 600;
    }

    .role-pill {
        display: inline-block;
        background: rgba(14, 165, 233, 0.15);
        color: #e0f2fe;
        border: 1px solid rgba(224, 242, 254, 0.28);
        border-radius: 999px;
        padding: 0.6rem 1.05rem;
        font-weight: 850;
        font-size: 0.95rem;
        white-space: nowrap;
    }

    .logout-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #0ea5e9;
        color: white !important;
        text-decoration: none !important;
        border-radius: 999px;
        padding: 0.6rem 1.05rem;
        font-weight: 850;
        font-size: 0.95rem;
        white-space: nowrap;
        box-shadow: 0 8px 18px rgba(14, 165, 233, 0.22);
    }

    .logout-link:hover {
        background: #0284c7;
        color: white !important;
        text-decoration: none !important;
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
        background: transparent;
        border-radius: 18px;
        padding: 0 0 2.2rem 0;
        width: 100%;
        max-width: 640px;
        margin: 0 auto 1.5rem auto;
        box-shadow: none;
        border: none;
    }

    .login-title {
        font-size: clamp(3.3rem, 5vw, 5.2rem);
        font-weight: 950;
        color: #020617;
        margin-bottom: 0.8rem;
        line-height: 0.95;
        letter-spacing: -0.065em;
        text-align: center;
    }

    .login-subtitle {
        color: #64748b;
        font-size: 1.08rem;
        margin-bottom: 0rem;
        text-align: center;
        font-weight: 650;
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
        margin-bottom: 0rem;
    }

    .admin-help {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
        line-height: 1.55;
    }

    .search-header-box,
    .results-header-box,
    .stats-header-box {
        background: white;
        border-radius: 16px;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.07);
        border: 1px solid rgba(229, 231, 235, 0.75);
        margin-top: 1.6rem;
    }

    .search-header-box {
        padding: 1.05rem 1.7rem;
        margin-bottom: 1.35rem;
    }

    .results-header-box {
        padding: 1.05rem 1.7rem;
        margin-bottom: 0.75rem;
    }

    .stats-header-box {
        padding: 0.9rem 1.7rem;
        margin-top: 3.4rem;
        margin-bottom: 1.5rem;
    }

    .search-header-box .panel-title {
        margin-bottom: 0.35rem;
    }

    .results-header-box .panel-title,
    .stats-header-box .panel-title {
        margin-bottom: 0rem;
    }

    .chart-title {
        font-size: 1.2rem;
        font-weight: 850;
        color: #1f2937;
        margin-bottom: 0.55rem;
        line-height: 1.25;
    }

    .chart-row-spacer {
        height: 2.3rem;
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
        padding: 0.65rem 0.95rem;
        font-weight: 800;
        box-shadow: 0 8px 18px rgba(14,165,233,0.22);
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
        width: 100%;
        max-width: 100%;
        min-height: 2.65rem;
        font-size: clamp(0.78rem, 0.85vw, 0.95rem);
    }

    div.stButton > button:first-child p {
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
    }

    div.stButton > button:first-child:hover {
        background: #0284c7;
        color: white;
        border: 0;
    }

    div[data-testid="stSelectbox"] > div,
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextArea"] > div,
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stDateInput"] > div,
    div[data-testid="stTimeInput"] > div {
        border-radius: 10px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    .section-separator {
        height: 1rem;
    }

    .section-large-spacer {
        height: 1.4rem;
    }

    @media (max-width: 900px) {
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        .topbar {
            align-items: flex-start;
            gap: 1rem;
            flex-direction: column;
        }

        .topbar-actions {
            flex-wrap: wrap;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Authentification et droits
# ------------------------------------------------------------

def normalize_role(role):
    """Convertit les anciens noms de rôles vers les nouveaux."""
    if role == "client":
        return "visiteur"

    if role == "employe_capitaine":
        return "employe"

    return role


def is_logged_in():
    """Vérifie si l'utilisateur est connecté."""
    return st.session_state.get("authenticated", False)


def get_current_role():
    """Renvoie le rôle courant."""
    return normalize_role(st.session_state.get("role", "visiteur"))


def get_current_role_label():
    """Renvoie le libellé du rôle courant."""
    role = get_current_role()
    return ROLE_LABELS.get(role, "Utilisateur")


def can_view_sql():
    """Le visiteur ne voit pas les requêtes SQL avancées."""
    return get_current_role() in ["employe", "administrateur"]


def can_export_results():
    """Les employés/capitaines et administrateurs peuvent exporter."""
    return get_current_role() in ["employe", "administrateur"]


def is_admin():
    """Vérifie si l'utilisateur est administrateur."""
    return get_current_role() == "administrateur"


def handle_logout_from_url():
    """Déconnecte l'utilisateur si le lien ?logout=1 est utilisé."""
    if st.query_params.get("logout") == "1":
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.role_label = None
        st.query_params.clear()
        st.rerun()


def reset_search_filters():
    """Remet les filtres de recherche à leur état initial."""
    for key, value in SEARCH_DEFAULTS.items():
        st.session_state[key] = value


def login_screen():
    """Affiche l'écran de connexion avec une image de fond et une carte à droite."""
    background_url = get_login_background_data_url()

    if background_url:
        background_css = f"""
            background-image:
                linear-gradient(90deg, rgba(2, 6, 23, 0.04), rgba(2, 6, 23, 0.28)),
                url("{background_url}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
        """
    else:
        background_css = """
            background:
                linear-gradient(90deg, rgba(2, 6, 23, 0.05), rgba(2, 6, 23, 0.25)),
                linear-gradient(135deg, #bae6fd 0%, #38bdf8 45%, #075985 100%) !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
        """

    st.markdown(
        """
        <style>
        .stApp {
        """
        + background_css
        + """
        }

        .block-container {
            padding-top: clamp(1.5rem, 4vh, 3rem) !important;
            padding-bottom: clamp(1.5rem, 4vh, 3rem) !important;
            padding-left: clamp(2rem, 4vw, 4rem) !important;
            padding-right: clamp(2rem, 4vw, 4rem) !important;
        }

        div[data-testid="stForm"] {
            min-height: clamp(620px, 82vh, 780px);
            height: clamp(620px, 82vh, 780px);
            width: 100%;
            max-width: 760px;
            margin-left: auto;
            margin-right: 0;

            border-radius: 24px;
            background: rgba(248, 250, 252, 0.96);
            border: 1px solid rgba(226, 232, 240, 0.95);

            box-shadow:
                0 34px 90px rgba(2, 6, 23, 0.44),
                0 14px 32px rgba(2, 6, 23, 0.26);

            padding: clamp(2.5rem, 5vw, 4.8rem);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        div[data-testid="stForm"] > div {
            width: 100%;
            max-width: 620px;
            margin-left: auto;
            margin-right: auto;
        }

        div[data-testid="stForm"] label {
            color: #334155 !important;
            font-weight: 650 !important;
        }

        div[data-testid="stForm"] input {
            border-radius: 10px !important;
            background: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
            min-height: 2.75rem !important;
        }

        div[data-testid="stFormSubmitButton"] button {
            background: #0ea5e9 !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 800 !important;
            min-height: 2.9rem !important;
            box-shadow: 0 10px 22px rgba(14, 165, 233, 0.28);
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            background: #0284c7 !important;
            color: white !important;
        }

        .login-demo-box {
            margin-top: 1.5rem;
            background: rgba(248, 250, 252, 0.9);
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 1rem 1.1rem;
            color: #334155;
            font-size: 0.95rem;
        }

        .login-demo-box summary {
            cursor: pointer;
            font-weight: 800;
            color: #1e293b;
        }

        .login-demo-content {
            margin-top: 0.8rem;
            line-height: 1.7;
        }

        @media (max-width: 900px) {
            div[data-testid="stForm"] {
                min-height: auto;
                height: auto;
                max-width: 100%;
                margin-left: auto;
                margin-right: auto;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1.05, 1], gap="large")

    with left_col:
        st.empty()

    with right_col:
        with st.form("login_form"):
            st.markdown(
                """
                <div class="login-card">
                    <div class="login-title">ShipDATA</div>
                    <div class="login-subtitle">
                        Connecte-toi pour accéder à l'interface adaptée à ton rôle
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.session_state.get("login_error", False):
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter", use_container_width=True)

            st.markdown(
                """
                <div class="login-demo-box">
                    <details>
                        <summary>Comptes de démonstration</summary>
                        <div class="login-demo-content">
                            Visiteur : <code>visiteur</code> / <code>visiteur123</code><br>
                            Employé / capitaine : <code>employe</code> / <code>employe123</code><br>
                            Administrateur : <code>admin</code> / <code>admin123</code>
                        </div>
                    </details>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if submit:
        user = USERS.get(username.strip().lower())

        if user and password == user["password"]:
            st.session_state.login_error = False
            st.session_state.authenticated = True
            st.session_state.username = username.strip().lower()
            st.session_state.role = user["role"]
            st.session_state.role_label = user["label"]
            reset_search_filters()
            st.rerun()

        st.session_state.login_error = True
        st.rerun()


# ------------------------------------------------------------
# Connexion PostgreSQL
# ------------------------------------------------------------

def read_config():
    """Lit config.json à la racine du projet."""
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
        database=config.get("database", "shipdata"),
    )


def rollback_connection():
    """Annule une transaction PostgreSQL en erreur si nécessaire."""
    try:
        get_connection().rollback()
    except Exception:
        pass


def run_query(sql, params=None):
    """Exécute une requête SQL et renvoie un DataFrame."""
    conn = get_connection()
    return pd.read_sql_query(sql, conn, params=params)


def safe_query(sql, params=None):
    """Renvoie un DataFrame vide si une requête échoue."""
    try:
        return run_query(sql, params)
    except Exception:
        rollback_connection()
        return pd.DataFrame()


def execute_write_query(sql, params=None):
    """Exécute une requête d'écriture et valide la transaction."""
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or [])
        conn.commit()
    except Exception:
        conn.rollback()
        raise


# ------------------------------------------------------------
# Fonctions utilitaires
# ------------------------------------------------------------

def safe_count(table_name):
    """Compte les lignes d'une table."""
    try:
        return int(run_query(f"SELECT COUNT(*) AS n FROM {table_name}")["n"].iloc[0])
    except Exception:
        rollback_connection()
        return 0


def dataframe_auto_height(df, min_height=160, max_height=420, row_height=35):
    """Calcule une hauteur adaptée au nombre de lignes du tableau."""
    if df is None or df.empty:
        return min_height

    height = row_height * (len(df) + 1)
    return max(min_height, min(height, max_height))


def format_meter_value(value):
    """Ajoute l'unité m aux valeurs de dimensions."""
    if pd.isna(value) or value == "":
        return ""

    try:
        return f"{float(value):g} m"
    except Exception:
        return str(value)


def format_display_cell(value):
    """Convertit les valeurs pour forcer un affichage aligné à gauche."""
    if pd.isna(value):
        return ""

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:g}"

    return str(value)


def left_align_dataframe(df):
    """Transforme toutes les valeurs en texte pour éviter l'alignement à droite."""
    if df is None or df.empty:
        return df

    display_df = df.copy()

    for column in display_df.columns:
        display_df[column] = display_df[column].apply(format_display_cell)

    return display_df


def style_table_left(display_df):
    """Style neutre et aligné à gauche pour tous les tableaux."""
    if display_df is None or display_df.empty:
        return display_df

    return (
        display_df.style
        .set_properties(**{"text-align": "left"})
        .set_table_styles(
            [
                {"selector": "th", "props": [("text-align", "left")]},
                {"selector": "td", "props": [("text-align", "left")]},
            ]
        )
    )


def get_distinct_values(sql, placeholder):
    """Récupère des valeurs distinctes pour un menu déroulant."""
    df = safe_query(sql)

    if df.empty:
        return [placeholder]

    values = df.iloc[:, 0].dropna().astype(str).tolist()
    return [placeholder] + values


def initialize_search_state():
    """Crée les clés de session nécessaires aux filtres."""
    for key, value in SEARCH_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def ensure_filter_values_exist(type_values, pavillon_values, classification_values):
    """Évite les valeurs invalides dans les filtres."""
    initialize_search_state()

    if st.session_state.selected_type not in type_values:
        st.session_state.selected_type = "Type de navire"

    if st.session_state.selected_pavillon not in pavillon_values:
        st.session_state.selected_pavillon = "Pavillon"

    if st.session_state.selected_classification not in classification_values:
        st.session_state.selected_classification = "Société de classification"


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
                    labelLimit=160,
                ),
            ),
            y=alt.Y(
                f"{y_col}:Q",
                title=None,
                axis=alt.Axis(labelPadding=10),
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
                "bottom": 70,
            },
        )
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(chart, use_container_width=True)


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

    if role == "visiteur":
        wanted_columns = [
            "IMO",
            "Nom du navire",
            "Type",
            "Année",
            "Pavillon",
            "Longueur",
        ]
    elif role == "employe":
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

    return left_align_dataframe(display_df)


# ------------------------------------------------------------
# Requêtes SQL
# ------------------------------------------------------------

def build_main_query(search_text, type_filter, pavillon_filter, class_filter):
    """Construit la requête principale de recherche."""
    params = []
    where_parts = []

    sql = """
        SELECT
            n.imo,
            n.mmsi,
            n.nom_navire,
            t.nom_type AS type_navire,
            n.annee_construction,
            p.nom_pays AS pavillon,
            n.gross_tonnage AS gt,
            n.deadweight_tonnage AS dwt,
            n.longueur_m AS longueur,
            n.largeur_m AS largeur,
            n.tirant_eau_m AS tirant_eau,
            sc.nom_societe AS classification,
            co.nom_constructeur AS constructeur,
            pr.nom_proprietaire AS proprietaire
        FROM navire n
        LEFT JOIN type_navire t
            ON n.id_type_navire = t.id_type_navire
        LEFT JOIN pavillon p
            ON n.id_pavillon = p.id_pavillon
        LEFT JOIN societe_classification sc
            ON n.id_societe_classification = sc.id_societe_classification
        LEFT JOIN constructeur co
            ON n.id_constructeur = co.id_constructeur
        LEFT JOIN propriete_navire pn
            ON n.imo = pn.imo AND pn.date_fin IS NULL
        LEFT JOIN proprietaire pr
            ON pn.id_proprietaire = pr.id_proprietaire
    """

    if search_text.strip():
        search_value = f"%{search_text.strip()}%"
        where_parts.append(
            """
            (
                CAST(n.imo AS TEXT) ILIKE %s
                OR CAST(n.mmsi AS TEXT) ILIKE %s
                OR n.nom_navire ILIKE %s
            )
            """
        )
        params.extend([search_value, search_value, search_value])

    if type_filter != "Type de navire":
        where_parts.append("t.nom_type = %s")
        params.append(type_filter)

    if pavillon_filter != "Pavillon":
        where_parts.append("p.nom_pays = %s")
        params.append(pavillon_filter)

    if class_filter != "Société de classification":
        where_parts.append("sc.nom_societe = %s")
        params.append(class_filter)

    if where_parts:
        sql += " WHERE " + " AND ".join(where_parts)

    sql += " ORDER BY n.annee_construction ASC NULLS LAST LIMIT 50;"

    return sql, params


def predefined_queries():
    """Requêtes SQL visibles pour les employés/capitaines et administrateurs."""
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
    """Autorise seulement les requêtes SELECT/WITH sans modification."""
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

    for keyword in forbidden_keywords:
        if re.search(rf"\b{keyword}\b", cleaned):
            return False

    return True


# ------------------------------------------------------------
# Configuration de la gestion admin
# ------------------------------------------------------------

TABLE_CONFIGS = {
    "categorie_principale": {
        "label": "Catégories principales",
        "primary_key": ["id_categorie"],
        "display_columns": ["id_categorie", "nom_categorie"],
        "fields": [
            {"name": "id_categorie", "label": "ID catégorie", "type": "int", "required": True, "auto_next": True},
            {"name": "nom_categorie", "label": "Nom de la catégorie", "type": "text", "required": True},
            {"name": "description", "label": "Description", "type": "textarea", "required": True},
        ],
    },
    "type_navire": {
        "label": "Types de navires",
        "primary_key": ["id_type_navire"],
        "display_columns": ["id_type_navire", "nom_type"],
        "fields": [
            {"name": "id_type_navire", "label": "ID type", "type": "int", "required": True, "auto_next": True},
            {"name": "nom_type", "label": "Nom du type", "type": "text", "required": True},
            {
                "name": "id_categorie",
                "label": "Catégorie principale",
                "type": "fk",
                "required": True,
                "fk_table": "categorie_principale",
                "fk_id": "id_categorie",
                "fk_label": "nom_categorie",
            },
            {"name": "description", "label": "Description", "type": "textarea", "required": True},
        ],
    },
    "pavillon": {
        "label": "Pavillons",
        "primary_key": ["id_pavillon"],
        "display_columns": ["id_pavillon", "nom_pays"],
        "fields": [
            {"name": "id_pavillon", "label": "ID pavillon", "type": "int", "required": True, "auto_next": True},
            {"name": "nom_pays", "label": "Nom du pays", "type": "text", "required": True},
            {"name": "code_iso2", "label": "Code ISO2", "type": "text", "required": False},
            {"name": "code_iso3", "label": "Code ISO3", "type": "text", "required": True},
        ],
    },
    "societe_classification": {
        "label": "Sociétés de classification",
        "primary_key": ["id_societe_classification"],
        "display_columns": ["id_societe_classification", "nom_societe"],
        "fields": [
            {"name": "id_societe_classification", "label": "ID société", "type": "int", "required": True, "auto_next": True},
            {"name": "nom_societe", "label": "Nom de la société", "type": "text", "required": True},
            {"name": "sigle", "label": "Sigle", "type": "text", "required": True},
            {"name": "code_iso2_pays", "label": "Code ISO2 du pays", "type": "text", "required": True},
            {"name": "site_web", "label": "Site web", "type": "text", "required": True},
        ],
    },
    "port": {
        "label": "Ports",
        "primary_key": ["id_port"],
        "display_columns": ["id_port", "nom_port"],
        "fields": [
            {"name": "id_port", "label": "ID port", "type": "int", "required": True, "auto_next": True},
            {"name": "nom_port", "label": "Nom du port", "type": "text", "required": True},
            {"name": "nom_formel", "label": "Nom formel", "type": "text", "required": True},
            {"name": "code_iso2_pays", "label": "Code ISO2 du pays", "type": "text", "required": True},
            {"name": "latitude", "label": "Latitude", "type": "numeric", "required": True},
            {"name": "longitude", "label": "Longitude", "type": "numeric", "required": True},
            {
                "name": "taille_port",
                "label": "Taille du port",
                "type": "choice",
                "required": True,
                "choices": ["Very Small", "Small", "Medium", "Large"],
            },
            {
                "name": "type_port",
                "label": "Type de port",
                "type": "choice",
                "required": True,
                "choices": [
                    "Coastal Breakwater",
                    "Coastal Natural",
                    "Coastal Tide Gate",
                    "Lake or Canal",
                    "Open Roadstead",
                    "River Basin",
                    "River Natural",
                    "River Tide Gate",
                ],
            },
            {
                "name": "capacite_max_navire",
                "label": "Capacité max navire",
                "type": "choice",
                "required": True,
                "choices": ["Over 500'", "Under 500'"],
            },
        ],
    },
    "constructeur": {
        "label": "Constructeurs",
        "primary_key": ["id_constructeur"],
        "display_columns": ["id_constructeur", "nom_constructeur"],
        "fields": [
            {"name": "id_constructeur", "label": "ID constructeur", "type": "int", "required": True, "auto_next": True},
            {"name": "nom_constructeur", "label": "Nom du constructeur", "type": "text", "required": True},
            {"name": "code_iso2_pays", "label": "Code ISO2 du pays", "type": "text", "required": True},
            {"name": "annee_fondation", "label": "Année de fondation", "type": "int", "required": True},
            {"name": "ville_chantier", "label": "Ville du chantier", "type": "text", "required": True},
        ],
    },
    "proprietaire": {
        "label": "Propriétaires",
        "primary_key": ["id_proprietaire"],
        "display_columns": ["id_proprietaire", "nom_proprietaire"],
        "fields": [
            {"name": "id_proprietaire", "label": "ID propriétaire", "type": "int", "required": True, "auto_next": True},
            {"name": "nom_proprietaire", "label": "Nom du propriétaire", "type": "text", "required": True},
            {"name": "code_iso2_pays", "label": "Code ISO2 du pays", "type": "text", "required": True},
            {"name": "annee_creation", "label": "Année de création", "type": "int", "required": True},
            {"name": "ville_siege", "label": "Ville du siège", "type": "text", "required": True},
        ],
    },
    "navire": {
        "label": "Navires",
        "primary_key": ["imo"],
        "display_columns": ["imo", "nom_navire"],
        "fields": [
            {"name": "imo", "label": "IMO", "type": "int", "required": True},
            {"name": "mmsi", "label": "MMSI", "type": "int", "required": True},
            {"name": "nom_navire", "label": "Nom du navire", "type": "text", "required": True},
            {
                "name": "id_type_navire",
                "label": "Type de navire",
                "type": "fk",
                "required": True,
                "fk_table": "type_navire",
                "fk_id": "id_type_navire",
                "fk_label": "nom_type",
            },
            {
                "name": "id_pavillon",
                "label": "Pavillon",
                "type": "fk",
                "required": True,
                "fk_table": "pavillon",
                "fk_id": "id_pavillon",
                "fk_label": "nom_pays",
            },
            {"name": "annee_construction", "label": "Année de construction", "type": "int", "required": True},
            {"name": "gross_tonnage", "label": "Gross tonnage", "type": "int", "required": True},
            {"name": "deadweight_tonnage", "label": "Deadweight tonnage", "type": "int", "required": True},
            {"name": "longueur_m", "label": "Longueur en m", "type": "numeric", "required": True},
            {"name": "largeur_m", "label": "Largeur en m", "type": "numeric", "required": True},
            {"name": "tirant_eau_m", "label": "Tirant d'eau en m", "type": "numeric", "required": True},
            {
                "name": "id_societe_classification",
                "label": "Société de classification",
                "type": "fk",
                "required": True,
                "fk_table": "societe_classification",
                "fk_id": "id_societe_classification",
                "fk_label": "nom_societe",
            },
            {
                "name": "id_constructeur",
                "label": "Constructeur",
                "type": "fk",
                "required": True,
                "fk_table": "constructeur",
                "fk_id": "id_constructeur",
                "fk_label": "nom_constructeur",
            },
        ],
    },
    "propriete_navire": {
        "label": "Propriétés des navires",
        "primary_key": ["imo", "id_proprietaire", "date_debut"],
        "display_columns": ["imo", "id_proprietaire", "date_debut"],
        "fields": [
            {
                "name": "imo",
                "label": "Navire",
                "type": "fk",
                "required": True,
                "fk_table": "navire",
                "fk_id": "imo",
                "fk_label": "nom_navire",
            },
            {
                "name": "id_proprietaire",
                "label": "Propriétaire",
                "type": "fk",
                "required": True,
                "fk_table": "proprietaire",
                "fk_id": "id_proprietaire",
                "fk_label": "nom_proprietaire",
            },
            {"name": "date_debut", "label": "Date de début", "type": "date", "required": True},
            {"name": "date_fin", "label": "Date de fin", "type": "date", "required": False},
        ],
    },
    "escale": {
        "label": "Escales",
        "primary_key": ["id_escale"],
        "display_columns": ["id_escale", "imo", "id_port", "date_arrivee"],
        "fields": [
            {"name": "id_escale", "label": "ID escale", "type": "int", "required": True, "auto_next": True},
            {
                "name": "imo",
                "label": "Navire",
                "type": "fk",
                "required": True,
                "fk_table": "navire",
                "fk_id": "imo",
                "fk_label": "nom_navire",
            },
            {
                "name": "id_port",
                "label": "Port",
                "type": "fk",
                "required": True,
                "fk_table": "port",
                "fk_id": "id_port",
                "fk_label": "nom_port",
            },
            {"name": "date_arrivee", "label": "Date d'arrivée", "type": "date", "required": True},
            {"name": "heure_arrivee", "label": "Heure d'arrivée", "type": "time", "required": False},
            {"name": "date_depart", "label": "Date de départ", "type": "date", "required": False},
            {"name": "heure_depart", "label": "Heure de départ", "type": "time", "required": False},
        ],
    },
}


def get_next_id(table_name, column_name):
    """Propose l'identifiant suivant pour les tables sans séquence SQL."""
    df = safe_query(f"SELECT COALESCE(MAX({column_name}), 0) + 1 AS next_id FROM {table_name};")

    if df.empty:
        return 1

    return int(df["next_id"].iloc[0])


def get_fk_options(field):
    """Récupère les valeurs possibles pour une clé étrangère."""
    table_name = field["fk_table"]
    id_column = field["fk_id"]
    label_column = field["fk_label"]

    df = safe_query(
        f"""
        SELECT {id_column} AS id_value, {label_column} AS label_value
        FROM {table_name}
        ORDER BY {label_column};
        """
    )

    if df.empty:
        return []

    options = []

    for _, row in df.iterrows():
        value = row["id_value"]
        label = row["label_value"]
        options.append((value, f"{value} - {label}"))

    return options


def clean_value(value):
    """Nettoie les valeurs venant de pandas."""
    if pd.isna(value):
        return None

    return value


def to_python_date(value):
    """Convertit une valeur en date Python."""
    value = clean_value(value)

    if value is None:
        return date.today()

    if isinstance(value, date):
        return value

    return pd.to_datetime(value).date()


def to_python_time(value):
    """Convertit une valeur en heure Python."""
    value = clean_value(value)

    if value is None:
        return time(0, 0)

    if isinstance(value, time):
        return value

    return pd.to_datetime(str(value)).time()


def input_admin_field(field, key_prefix, table_name, current_value=None, disabled=False):
    """Crée le widget Streamlit adapté à un champ admin."""
    name = field["name"]
    label = field["label"]
    field_type = field["type"]
    required = field.get("required", True)
    value = clean_value(current_value)
    key = f"{key_prefix}_{name}"

    if field_type == "int":
        if value is None:
            value = get_next_id(table_name, name) if field.get("auto_next") else 0

        return int(st.number_input(label, value=int(value), step=1, disabled=disabled, key=key))

    if field_type == "numeric":
        if value is None:
            value = 0.0

        return float(
            st.number_input(
                label,
                value=float(value),
                step=0.01,
                format="%.6f",
                disabled=disabled,
                key=key,
            )
        )

    if field_type == "text":
        default_value = "" if value is None else str(value)
        result = st.text_input(label, value=default_value, disabled=disabled, key=key).strip()
        return None if (not required and result == "") else result

    if field_type == "textarea":
        default_value = "" if value is None else str(value)
        result = st.text_area(label, value=default_value, height=90, disabled=disabled, key=key).strip()
        return None if (not required and result == "") else result

    if field_type == "choice":
        choices = field.get("choices", [])
        index = choices.index(value) if value in choices else 0
        return st.selectbox(label, choices, index=index, disabled=disabled, key=key)

    if field_type == "fk":
        options = get_fk_options(field)

        if not options:
            st.warning(f"Aucune valeur disponible pour : {label}")
            return None

        option_values = [option[0] for option in options]
        index = option_values.index(value) if value in option_values else 0

        selected = st.selectbox(
            label,
            options,
            index=index,
            format_func=lambda option: option[1],
            disabled=disabled,
            key=key,
        )

        return selected[0]

    if field_type == "date":
        if not required:
            empty_value = value is None
            is_empty = st.checkbox(
                f"{label} vide",
                value=empty_value,
                disabled=disabled,
                key=f"{key}_empty",
            )

            if is_empty:
                return None

        return st.date_input(label, value=to_python_date(value), disabled=disabled, key=key)

    if field_type == "time":
        if not required:
            empty_value = value is None
            is_empty = st.checkbox(
                f"{label} vide",
                value=empty_value,
                disabled=disabled,
                key=f"{key}_empty",
            )

            if is_empty:
                return None

        return st.time_input(label, value=to_python_time(value), disabled=disabled, key=key)

    return None


def row_label(row, display_columns):
    """Construit un libellé lisible pour une ligne."""
    parts = []

    for column in display_columns:
        if column in row:
            parts.append(str(row[column]))

    return " | ".join(parts)


def get_table_rows(table_name, config):
    """Charge les lignes d'une table pour la modification."""
    columns_sql = ", ".join(config["display_columns"])
    order_sql = ", ".join(config["primary_key"])

    return safe_query(
        f"""
        SELECT {columns_sql}
        FROM {table_name}
        ORDER BY {order_sql}
        LIMIT 300;
        """
    )


def get_full_row(table_name, config, selected_row):
    """Charge toutes les colonnes d'une ligne sélectionnée."""
    where_parts = []
    params = []

    for pk_column in config["primary_key"]:
        where_parts.append(f"{pk_column} = %s")
        params.append(selected_row[pk_column])

    where_sql = " AND ".join(where_parts)

    return safe_query(
        f"""
        SELECT *
        FROM {table_name}
        WHERE {where_sql}
        LIMIT 1;
        """,
        params=params,
    )


def validate_admin_values(config, values):
    """Vérifie que les champs obligatoires sont remplis."""
    errors = []

    for field in config["fields"]:
        name = field["name"]
        value = values.get(name)

        if field.get("required", True) and value in [None, ""]:
            errors.append(f"Le champ « {field['label']} » est obligatoire.")

    return errors


def insert_admin_row(table_name, config, values):
    """Ajoute une ligne dans la table sélectionnée."""
    columns = [field["name"] for field in config["fields"]]
    placeholders = ", ".join(["%s"] * len(columns))
    columns_sql = ", ".join(columns)

    sql = f"""
        INSERT INTO {table_name} ({columns_sql})
        VALUES ({placeholders});
    """

    params = [values[column] for column in columns]
    execute_write_query(sql, params)


def update_admin_row(table_name, config, values, original_pk_values):
    """Modifie une ligne existante dans la table sélectionnée."""
    primary_key = config["primary_key"]
    editable_columns = [
        field["name"]
        for field in config["fields"]
        if field["name"] not in primary_key
    ]

    if not editable_columns:
        return

    set_sql = ", ".join([f"{column} = %s" for column in editable_columns])
    where_sql = " AND ".join([f"{column} = %s" for column in primary_key])

    sql = f"""
        UPDATE {table_name}
        SET {set_sql}
        WHERE {where_sql};
    """

    params = [values[column] for column in editable_columns]
    params.extend([original_pk_values[column] for column in primary_key])

    execute_write_query(sql, params)


def show_admin_data_management():
    """Affiche la section admin pour ajouter ou modifier les données."""
    st.markdown(
        """
        <div class="panel-title" style="margin-top:2rem;">Gestion des données</div>
        <div class="admin-help">
            Cette section est réservée à l'administrateur. Elle permet d'ajouter de nouvelles lignes
            dans les tables principales ou de modifier des lignes existantes. Les contraintes PostgreSQL
            restent actives : clés primaires, clés étrangères, valeurs uniques et contrôles de domaine.
        </div>
        """,
        unsafe_allow_html=True,
    )

    add_tab, edit_tab = st.tabs(["Ajouter une donnée", "Modifier une donnée"])
    table_names = list(TABLE_CONFIGS.keys())

    with add_tab:
        selected_table = st.selectbox(
            "Table à compléter",
            table_names,
            format_func=lambda table: TABLE_CONFIGS[table]["label"],
            key="admin_add_table",
        )

        config = TABLE_CONFIGS[selected_table]

        with st.form(f"add_form_{selected_table}"):
            values = {}

            for field in config["fields"]:
                values[field["name"]] = input_admin_field(
                    field,
                    key_prefix=f"add_{selected_table}",
                    table_name=selected_table,
                )

            submit_add = st.form_submit_button("Ajouter la donnée", use_container_width=True)

        if submit_add:
            errors = validate_admin_values(config, values)

            if errors:
                for error in errors:
                    st.warning(error)
            else:
                try:
                    insert_admin_row(selected_table, config, values)
                    st.success("La donnée a été ajoutée avec succès.")
                except Exception as error:
                    st.error("Impossible d'ajouter cette donnée.")
                    st.exception(error)

    with edit_tab:
        selected_table_edit = st.selectbox(
            "Table à modifier",
            table_names,
            format_func=lambda table: TABLE_CONFIGS[table]["label"],
            key="admin_edit_table",
        )

        config = TABLE_CONFIGS[selected_table_edit]
        rows = get_table_rows(selected_table_edit, config)

        if rows.empty:
            st.info("Aucune donnée disponible dans cette table.")
        else:
            row_indices = list(range(len(rows)))

            selected_index = st.selectbox(
                "Ligne à modifier",
                row_indices,
                format_func=lambda index: row_label(rows.iloc[index], config["display_columns"]),
                key=f"admin_edit_row_{selected_table_edit}",
            )

            selected_row = rows.iloc[selected_index]
            full_row_df = get_full_row(selected_table_edit, config, selected_row)

            if full_row_df.empty:
                st.warning("Impossible de charger la ligne sélectionnée.")
            else:
                full_row = full_row_df.iloc[0]
                original_pk_values = {
                    pk_column: full_row[pk_column]
                    for pk_column in config["primary_key"]
                }

                with st.form(f"edit_form_{selected_table_edit}_{selected_index}"):
                    values = {}

                    for field in config["fields"]:
                        field_name = field["name"]
                        is_primary_key = field_name in config["primary_key"]

                        values[field_name] = input_admin_field(
                            field,
                            key_prefix=f"edit_{selected_table_edit}_{selected_index}",
                            table_name=selected_table_edit,
                            current_value=full_row[field_name],
                            disabled=is_primary_key,
                        )

                    submit_edit = st.form_submit_button(
                        "Enregistrer les modifications",
                        use_container_width=True,
                    )

                if submit_edit:
                    errors = validate_admin_values(config, values)

                    if errors:
                        for error in errors:
                            st.warning(error)
                    else:
                        try:
                            update_admin_row(
                                selected_table_edit,
                                config,
                                values,
                                original_pk_values,
                            )
                            st.success("Les modifications ont été enregistrées.")
                        except Exception as error:
                            st.error("Impossible de modifier cette donnée.")
                            st.exception(error)


# ------------------------------------------------------------
# Écran de connexion
# ------------------------------------------------------------

handle_logout_from_url()

if not is_logged_in():
    login_screen()
    st.stop()


# ------------------------------------------------------------
# Connexion à la base
# ------------------------------------------------------------

try:
    get_connection()
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
        <div class="topbar-actions">
            <div class="role-pill">{role_label}</div>
            <a class="logout-link" href="?logout=1" target="_self">Déconnexion</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-title">Tableau de bord maritime</div>
    <div class="hero-subtitle">
        Interface de consultation des navires, pavillons, constructeurs, propriétaires,
        ports, escales et sociétés de classification.
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Métriques
# ------------------------------------------------------------

navire_count = safe_count("navire")
pavillon_count = safe_count("pavillon")
port_count = safe_count("port")
classification_count = safe_count("societe_classification")

m1, m2, m3, m4 = st.columns([1, 1, 1, 1], gap="medium")

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
    <div class="search-header-box">
        <div class="panel-title">Recherche multicritère</div>
        <div class="panel-help">
            Les informations affichées changent selon le rôle connecté.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

type_values = get_distinct_values(
    "SELECT DISTINCT nom_type FROM type_navire ORDER BY nom_type;",
    "Type de navire",
)
pavillon_values = get_distinct_values(
    "SELECT DISTINCT nom_pays FROM pavillon ORDER BY nom_pays;",
    "Pavillon",
)
classification_values = get_distinct_values(
    "SELECT DISTINCT nom_societe FROM societe_classification ORDER BY nom_societe;",
    "Société de classification",
)

ensure_filter_values_exist(type_values, pavillon_values, classification_values)

if get_current_role() == "visiteur":
    c1, c2, c3 = st.columns([2.2, 1, 1], gap="medium")

    with c1:
        search_text = st.text_input(
            "Recherche",
            placeholder="Rechercher par nom, IMO ou MMSI...",
            label_visibility="collapsed",
            key="search_text",
        )

    with c2:
        selected_type = st.selectbox(
            "Type de navire",
            type_values,
            label_visibility="collapsed",
            key="selected_type",
        )

    with c3:
        selected_pavillon = st.selectbox(
            "Pavillon",
            pavillon_values,
            label_visibility="collapsed",
            key="selected_pavillon",
        )

    selected_classification = "Société de classification"

else:
    c1, c2, c3, c4 = st.columns([2.1, 1, 1, 1], gap="medium")

    with c1:
        search_text = st.text_input(
            "Recherche",
            placeholder="Rechercher par nom, IMO ou MMSI...",
            label_visibility="collapsed",
            key="search_text",
        )

    with c2:
        selected_type = st.selectbox(
            "Type de navire",
            type_values,
            label_visibility="collapsed",
            key="selected_type",
        )

    with c3:
        selected_pavillon = st.selectbox(
            "Pavillon",
            pavillon_values,
            label_visibility="collapsed",
            key="selected_pavillon",
        )

    with c4:
        selected_classification = st.selectbox(
            "Société de classification",
            classification_values,
            label_visibility="collapsed",
            key="selected_classification",
        )

if can_export_results():
    button_col_1, button_col_2, button_col_3, spacer = st.columns(
        [1.65, 1.45, 1.55, 4.35],
        gap="medium",
    )

    with button_col_1:
        st.button("Lancer la recherche", key="run_search")

    with button_col_2:
        st.button(
            "Réinitialiser",
            key="reset_search",
            on_click=reset_search_filters,
        )

    with button_col_3:
        export_placeholder = st.empty()

else:
    button_col_1, button_col_2, spacer = st.columns(
        [1.65, 1.45, 5.9],
        gap="medium",
    )

    with button_col_1:
        st.button("Lancer la recherche", key="run_search")

    with button_col_2:
        st.button(
            "Réinitialiser",
            key="reset_search",
            on_click=reset_search_filters,
        )

    export_placeholder = None

sql, params = build_main_query(
    search_text,
    selected_type,
    selected_pavillon,
    selected_classification,
)

try:
    results = run_query(sql, params)
except Exception as error:
    rollback_connection()
    st.error("Impossible d'exécuter la requête de recherche.")
    st.exception(error)
    results = pd.DataFrame()

if can_export_results() and export_placeholder is not None:
    if not results.empty:
        csv_data = results.to_csv(index=False).encode("utf-8")
        export_placeholder.download_button(
            label="Exporter CSV",
            data=csv_data,
            file_name="shipdata_resultats.csv",
            mime="text/csv",
        )
    else:
        export_placeholder.button("Exporter CSV", disabled=True)


# ------------------------------------------------------------
# Résultats
# ------------------------------------------------------------

st.markdown(
    """
    <div class="results-header-box">
        <div class="panel-title">Résultats de recherche</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if results.empty:
    st.info("Aucun résultat trouvé.")
else:
    display_results = prepare_display_dataframe(results)
    st.dataframe(
        style_table_left(display_results),
        use_container_width=True,
        hide_index=True,
        height=dataframe_auto_height(display_results, min_height=220, max_height=420),
    )

st.markdown('<div class="section-large-spacer"></div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# Statistiques rapides
# ------------------------------------------------------------

st.markdown(
    """
    <div class="stats-header-box">
        <div class="panel-title">Statistiques rapides</div>
    </div>
    """,
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns([1, 1], gap="medium")

with chart_col1:
    st.markdown(
        '<div class="chart-title">Répartition des navires par type</div>',
        unsafe_allow_html=True,
    )

    chart_df = safe_query(
        """
        SELECT t.nom_type AS type_navire, COUNT(*) AS nombre_navires
        FROM navire n
        JOIN type_navire t ON n.id_type_navire = t.id_type_navire
        GROUP BY t.nom_type
        ORDER BY nombre_navires DESC
        LIMIT 10;
        """
    )
    show_bar_chart_with_margins(chart_df, "type_navire", "nombre_navires")

with chart_col2:
    st.markdown(
        '<div class="chart-title">Top pavillons</div>',
        unsafe_allow_html=True,
    )

    chart_df = safe_query(
        """
        SELECT p.nom_pays AS pavillon, COUNT(*) AS nombre_navires
        FROM navire n
        JOIN pavillon p ON n.id_pavillon = p.id_pavillon
        GROUP BY p.nom_pays
        ORDER BY nombre_navires DESC
        LIMIT 10;
        """
    )
    show_bar_chart_with_margins(chart_df, "pavillon", "nombre_navires")

if get_current_role() in ["employe", "administrateur"]:
    st.markdown('<div class="chart-row-spacer"></div>', unsafe_allow_html=True)

    chart_col3, chart_col4 = st.columns([1, 1], gap="medium")

    with chart_col3:
        st.markdown(
            '<div class="chart-title">Constructeurs les plus représentés</div>',
            unsafe_allow_html=True,
        )

        chart_df = safe_query(
            """
            SELECT co.nom_constructeur AS constructeur, COUNT(*) AS nombre_navires
            FROM navire n
            JOIN constructeur co ON n.id_constructeur = co.id_constructeur
            GROUP BY co.nom_constructeur
            ORDER BY nombre_navires DESC
            LIMIT 10;
            """
        )
        show_bar_chart_with_margins(chart_df, "constructeur", "nombre_navires")

    with chart_col4:
        st.markdown(
            "<div class=\"chart-title\">Ports avec le plus d'escales</div>",
            unsafe_allow_html=True,
        )

        chart_df = safe_query(
            """
            SELECT p.nom_port AS port, COUNT(e.id_escale) AS nombre_escales
            FROM port p
            JOIN escale e ON e.id_port = p.id_port
            GROUP BY p.nom_port
            ORDER BY nombre_escales DESC
            LIMIT 10;
            """
        )
        show_bar_chart_with_margins(chart_df, "port", "nombre_escales")


# ------------------------------------------------------------
# Requêtes SQL prédéfinies
# ------------------------------------------------------------

if can_view_sql():
    queries = predefined_queries()
    query_titles = list(queries.keys())

    st.markdown('<div class="section-separator"></div>', unsafe_allow_html=True)
    left, right = st.columns([1, 1], gap="medium")

    with left:
        st.markdown(
            '<div class="panel"><div class="panel-title">Requêtes SQL disponibles</div>',
            unsafe_allow_html=True,
        )

        if "selected_query" not in st.session_state:
            st.session_state.selected_query = query_titles[0] if query_titles else None

        for title in query_titles:
            if st.button(title, key=f"query_{title}", use_container_width=True):
                st.session_state.selected_query = title

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="panel"><div class="panel-title">Aperçu SQL</div>',
            unsafe_allow_html=True,
        )

        selected_sql = queries.get(st.session_state.get("selected_query"), "")
        st.markdown(f'<div class="sql-box">{selected_sql}</div>', unsafe_allow_html=True)

        if selected_sql:
            if st.button("Exécuter cette requête", use_container_width=True):
                try:
                    query_result = run_query(selected_sql)
                    query_result_display = left_align_dataframe(query_result)

                    st.dataframe(
                        style_table_left(query_result_display),
                        use_container_width=True,
                        hide_index=True,
                        height=dataframe_auto_height(
                            query_result_display,
                            min_height=150,
                            max_height=320,
                        ),
                    )
                except Exception as error:
                    rollback_connection()
                    st.error("Impossible d'exécuter cette requête.")
                    st.exception(error)

        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# Requête personnalisée réservée à l'administrateur
# ------------------------------------------------------------

if is_admin():
    st.markdown(
        '<div class="panel"><div class="panel-title">Requête SELECT personnalisée</div>',
        unsafe_allow_html=True,
    )

    custom_sql = st.text_area(
        "Écrire une requête SQL",
        placeholder="SELECT * FROM navire LIMIT 10;",
        height=130,
    )

    if st.button("Exécuter la requête personnalisée"):
        if is_safe_select_query(custom_sql):
            try:
                custom_result = run_query(custom_sql)
                custom_result_display = left_align_dataframe(custom_result)

                st.dataframe(
                    style_table_left(custom_result_display),
                    use_container_width=True,
                    hide_index=True,
                    height=dataframe_auto_height(
                        custom_result_display,
                        min_height=150,
                        max_height=320,
                    ),
                )
            except Exception as error:
                rollback_connection()
                st.error("Impossible d'exécuter cette requête.")
                st.exception(error)
        else:
            st.warning("Seules les requêtes SELECT ou WITH sans modification de données sont autorisées.")

    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# Gestion des données réservée à l'administrateur
# ------------------------------------------------------------

if is_admin():
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    show_admin_data_management()
    st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# Structure de la base réservée à l'administrateur
# ------------------------------------------------------------

if is_admin():
    with st.expander("Voir la structure détectée de la base"):
        st.write("Tables principales :")
        st.write([
            "categorie_principale",
            "type_navire",
            "pavillon",
            "societe_classification",
            "port",
            "constructeur",
            "proprietaire",
            "navire",
            "propriete_navire",
            "escale",
        ])


# ------------------------------------------------------------
# Pied de page
# ------------------------------------------------------------

st.markdown(
    """
    <div style="text-align:center;color:#94a3b8;font-size:0.85rem;margin-top:2.5rem;">
        Projet de bases de données — ShipData — Interface Streamlit avec rôles utilisateur
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)