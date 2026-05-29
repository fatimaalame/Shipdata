from datetime import date, time
from html import escape
from pathlib import Path
import base64
from textwrap import dedent
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
# - propriétaire / proprio123
# - admin / admin123
#
# Le mode visiteur ne demande plus de compte : il est accessible
# depuis le bouton "Continuer en visiteur" sur la page de connexion.
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
    Trouve automatiquement la racine du projet sans dépendre
    d'un parents[1] ou parents[2].
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
APP_DIR = Path(__file__).resolve().parent
INTERFACE_DIR = APP_DIR / "INTERFACE"
CONFIG_PATH = ROOT_DIR / "config.json"

USERS = {
    "proprietaire": {
        "password": "proprio123",
        "role": "proprietaire",
        "label": "Propriétaire",
    },
    "propriétaire": {
        "password": "proprio123",
        "role": "proprietaire",
        "label": "Propriétaire",
    },
    "employe": {
        "password": "employe123",
        "role": "proprietaire",
        "label": "Propriétaire",
    },
    "capitaine": {
        "password": "capitaine123",
        "role": "proprietaire",
        "label": "Propriétaire",
    },
    "admin": {
        "password": "admin123",
        "role": "administrateur",
        "label": "Administrateur",
    },
}

ROLE_LABELS = {
    "visiteur": "Visiteur",
    "proprietaire": "Propriétaire",
    "administrateur": "Administrateur",
}

SEARCH_DEFAULTS = {
    "search_text": "",
    "selected_type": "Type de navire",
    "selected_pavillon": "Pavillon",
    "selected_classification": "Société de classification",
}


def render_html(markup):
    """Affiche du HTML sans que Streamlit le transforme en bloc de code."""
    st.markdown(dedent(str(markup)).strip(), unsafe_allow_html=True)


_ORIGINAL_ST_MARKDOWN = st.markdown

def safe_markdown(body, *args, **kwargs):
    """Déduplique l'indentation HTML pour éviter l'affichage du code brut."""
    if kwargs.get("unsafe_allow_html") and isinstance(body, str):
        body = dedent(body).strip()

    return _ORIGINAL_ST_MARKDOWN(body, *args, **kwargs)

st.markdown = safe_markdown

DEMO_OWNER_NAME = "Blue Harbor Maritime"
DEMO_OWNER_SHIP = "LEBANON STAR"
DEMO_OWNER_TEXT = (
    "Compte démo propriétaire : Blue Harbor Maritime possède le navire "
    "LEBANON STAR. Cette donnée est montrée dans l'interface pour la démonstration. "
    "Elle pourra ensuite être ajoutée dans les CSV ou dans PostgreSQL."
)

CSV_FILES = {
    "categorie_principale": "01_categorie_principale.csv",
    "type_navire": "02_type_navires.csv",
    "pavillon": "03_pavillons.csv",
    "societe_classification": "04_societes_classification.csv",
    "port": "05_port_data.csv",
    "constructeur": "06_constructeurs.csv",
    "proprietaire": "07_proprietaires.csv",
    "navire": "08_navires.csv",
    "propriete_navire": "09_propriete_navire.csv",
    "escale": "10_escales.csv",
}


# ------------------------------------------------------------
# Assets : logo et image de fond
# ------------------------------------------------------------

def image_to_base64(image_path):
    """Convertit une image locale en base64 pour l'utiliser dans le CSS."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def get_asset_data_url(candidate_names, fallback_mime="image/jpeg"):
    """Cherche une image dans le dossier INTERFACE, puis à côté du script."""
    search_dirs = [INTERFACE_DIR, APP_DIR, ROOT_DIR]

    mime_by_suffix = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        "": fallback_mime,
    }

    for directory in search_dirs:
        for name in candidate_names:
            image_path = directory / name
            if image_path.exists():
                suffix = image_path.suffix.lower()
                mime_type = mime_by_suffix.get(suffix, fallback_mime)
                encoded_image = image_to_base64(image_path)
                return f"data:{mime_type};base64,{encoded_image}"

    return None


def get_login_background_data_url():
    """Cherche l'image de fond de la page de connexion."""
    return get_asset_data_url(
        [
            "ProjetBD_Background.jpg",
            "ProjetBD_Background.jpeg",
            "ProjetBD_Background.png",
            "ProjetBD_Background.webp",
            "ProjetBD_Background",
        ],
        fallback_mime="image/jpeg",
    )


def get_logo_data_url():
    """Cherche le nouveau logo ShipData."""
    return get_asset_data_url(
        [
            "shipDATA logo.jpeg",
            "shipDATA logo.jpg",
            "shipDATA logo.png",
            "ShipDATA logo.jpeg",
            "ShipDATA logo.jpg",
            "ShipDATA logo.png",
            "shipdata_logo.jpeg",
            "shipdata_logo.jpg",
            "shipdata_logo.png",
            "ShipDATA_logo.jpeg",
            "ShipDATA_logo.jpg",
            "ShipDATA_logo.png",
            "logo.jpeg",
            "logo.jpg",
            "logo.png",
        ],
        fallback_mime="image/jpeg",
    )


def logo_markup(css_class="app-logo", dark=False):
    """Retourne le HTML du logo ou un fallback texte."""
    logo_url = get_logo_data_url()

    if logo_url:
        return f'<img class="{css_class}" src="{logo_url}" alt="ShipData logo">'

    color_class = "logo-fallback-dark" if dark else "logo-fallback-light"
    return f'<div class="{color_class}">SHIPDATA</div>'


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
        --navy: #235f7d;
        --navy-dark: #16435e;
        --blue: #0ea5e9;
        --cyan: #38bdf8;
        --mint: #10b981;
        --sand: #f4efe6;
        --cream: #fbfaf7;
        --bg: #f4f6f4;
        --card: #ffffff;
        --text: #141820;
        --muted: #64748b;
        --line: #e2e8f0;
        --warning-bg: #fff7ed;
        --warning-border: #f59e0b;
    }

    .stApp {
        background:
            radial-gradient(circle at 14% 8%, rgba(56, 189, 248, 0.13), transparent 25%),
            linear-gradient(180deg, #f8fafc 0%, #f1f5f2 100%);
        color: var(--text);
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .block-container {
        --page-x: clamp(2rem, 4.8vw, 5rem);
        padding-top: 0rem !important;
        padding-left: var(--page-x) !important;
        padding-right: var(--page-x) !important;
        padding-bottom: 3rem !important;
        max-width: 100% !important;
    }

    .main-content {
        padding: 0.45rem 0 3.2rem 0;
        margin-top: 6.2rem;
    }

    .topbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;

        background: linear-gradient(90deg, var(--navy-dark), var(--navy));
        color: white;
        padding: 0.9rem var(--page-x);

        display: flex;
        justify-content: space-between;
        align-items: center;

        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.22);
    }

    .topbar-left {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        min-width: 0;
    }

    .topbar-logo {
        display: block;
        width: clamp(150px, 16vw, 230px);
        max-height: 58px;
        object-fit: contain;
    }

    .logo-fallback-light {
        color: white;
        font-weight: 950;
        letter-spacing: -0.05em;
        font-size: 2rem;
        line-height: 1;
    }

    .logo-fallback-dark {
        color: #0f172a;
        font-weight: 950;
        letter-spacing: -0.05em;
        font-size: clamp(3rem, 5vw, 5rem);
        line-height: 1;
        text-align: center;
    }

    .topbar-nav {
        display: flex;
        align-items: center;
        gap: 1rem;
        color: #e5f3fb;
        font-weight: 650;
        font-size: 0.95rem;
    }

    .topbar-nav a {
        color: #e5f3fb !important;
        text-decoration: none !important;
        opacity: 0.94;
    }

    .topbar-nav a:hover {
        opacity: 1;
        color: #ffffff !important;
    }

    .user-menu {
        position: relative;
        display: inline-block;
    }

    .user-menu summary {
        list-style: none;
        cursor: pointer;
        user-select: none;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 999px;
        color: white;
        padding: 0.55rem 0.9rem;
        font-weight: 800;
        box-shadow: 0 8px 20px rgba(2, 6, 23, 0.16);
    }

    .user-menu summary::-webkit-details-marker {
        display: none;
    }

    .user-menu .chevron {
        display: inline-block;
        transition: transform 0.18s ease;
        font-size: 0.8rem;
        opacity: 0.85;
    }

    .user-menu[open] .chevron {
        transform: rotate(180deg);
    }

    .user-dropdown {
        position: absolute;
        right: 0;
        top: calc(100% + 0.75rem);
        width: 260px;
        background: #ffffff;
        border: 1px solid rgba(226, 232, 240, 0.95);
        border-radius: 18px;
        box-shadow: 0 22px 60px rgba(15, 23, 42, 0.24);
        padding: 0.55rem;
        overflow: hidden;
        animation: menuDrop 0.18s ease-out;
    }

    @keyframes menuDrop {
        from {
            opacity: 0;
            transform: translateY(-8px) scale(0.98);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .user-dropdown .account-line {
        color: #0f172a;
        background: #f1f5f9;
        border-radius: 13px;
        padding: 0.85rem 0.95rem;
        margin-bottom: 0.35rem;
        font-size: 0.88rem;
        line-height: 1.35;
        overflow-wrap: anywhere;
    }

    .user-dropdown .account-line strong {
        display: block;
        color: #0f172a;
        font-size: 0.98rem;
    }

    .user-dropdown a {
        display: block;
        color: #1f2937 !important;
        text-decoration: none !important;
        font-weight: 750;
        padding: 0.78rem 0.95rem;
        border-radius: 12px;
        transition: background 0.15s ease, transform 0.15s ease;
    }

    .user-dropdown a:hover {
        background: #e0f2fe;
        color: #075985 !important;
        transform: translateX(2px);
    }

    .hero-panel {
        background:
            linear-gradient(135deg, rgba(35, 95, 125, 0.96), rgba(14, 165, 233, 0.82)),
            radial-gradient(circle at 90% 15%, rgba(255, 255, 255, 0.3), transparent 22%);
        color: white;
        border-radius: 30px;
        padding: clamp(2rem, 4vw, 3.2rem);
        box-shadow: 0 26px 65px rgba(35, 95, 125, 0.26);
        margin-bottom: 1.8rem;
        overflow: hidden;
    }

    .hero-title {
        font-size: clamp(2.1rem, 4vw, 4rem);
        font-weight: 950;
        margin: 0 0 0.55rem 0;
        letter-spacing: -0.055em;
        line-height: 0.98;
    }

    .hero-subtitle {
        max-width: 820px;
        color: #e0f2fe;
        font-size: 1.05rem;
        line-height: 1.65;
        font-weight: 550;
        margin: 0;
    }

    .section-title {
        font-size: 1.55rem;
        font-weight: 900;
        color: #18212f;
        margin: 0 0 0.9rem 0;
        letter-spacing: -0.02em;
    }

    .section-help {
        color: var(--muted);
        font-size: 0.98rem;
        line-height: 1.6;
        margin-top: -0.4rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        border-radius: 22px;
        padding: 1.35rem 1.45rem;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.08);
        border: 1px solid rgba(226, 232, 240, 0.85);
        min-height: 120px;
        overflow: hidden;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.92rem;
        font-weight: 800;
        margin-bottom: 0.55rem;
        overflow-wrap: anywhere;
    }

    .metric-value {
        color: #111827;
        font-size: 2rem;
        font-weight: 950;
        letter-spacing: -0.04em;
        margin-bottom: 0.25rem;
        overflow-wrap: anywhere;
    }

    .metric-note {
        color: var(--mint);
        font-weight: 800;
        font-size: 0.88rem;
        overflow-wrap: anywhere;
    }

    .panel {
        background: white;
        border-radius: 24px;
        padding: clamp(1.25rem, 2vw, 1.8rem);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
        border: 1px solid rgba(226, 232, 240, 0.9);
        margin-top: 1.6rem;
        overflow: hidden;
    }

    .search-header-box,
    .results-header-box,
    .stats-header-box {
        background: white;
        border-radius: 22px;
        box-shadow: 0 14px 35px rgba(15, 23, 42, 0.07);
        border: 1px solid rgba(226, 232, 240, 0.85);
    }

    .search-header-box {
        padding: 1.1rem 1.45rem;
        margin-top: 1.8rem;
        margin-bottom: 1.25rem;
    }

    .results-header-box {
        padding: 1.1rem 1.45rem;
        margin-top: 1.75rem;
        margin-bottom: 0.9rem;
    }

    .stats-header-box {
        padding: 1.1rem 1.45rem;
        margin-top: 3.5rem;
        margin-bottom: 1.5rem;
    }

    .stats-grid-spacer {
        height: 0.9rem;
    }

    .chart-title {
        font-size: 1.16rem;
        font-weight: 900;
        color: #1f2937;
        margin-bottom: 0.7rem;
        line-height: 1.25;
    }

    .chart-row-spacer {
        height: 2.3rem;
    }

    .sql-box {
        background: #0b1020;
        color: #e5e7eb;
        border-radius: 16px;
        padding: 1.25rem;
        font-family: "SF Mono", Consolas, monospace;
        font-size: 0.86rem;
        line-height: 1.55;
        white-space: pre-wrap;
        overflow-x: auto;
        min-height: 430px;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
    }

    div.stButton > button:first-child,
    div[data-testid="stDownloadButton"] > button:first-child,
    div[data-testid="stFormSubmitButton"] button {
        background: var(--blue);
        color: white;
        border: 0;
        border-radius: 13px;
        padding: 0.65rem 0.95rem;
        font-weight: 850;
        box-shadow: 0 8px 18px rgba(14,165,233,0.22);
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
        width: 100%;
        max-width: 100%;
        min-height: 2.7rem;
        font-size: clamp(0.78rem, 0.85vw, 0.95rem);
    }

    div.stButton > button:first-child p,
    div[data-testid="stDownloadButton"] > button:first-child p,
    div[data-testid="stFormSubmitButton"] button p {
        white-space: nowrap !important;
        word-break: keep-all !important;
        overflow-wrap: normal !important;
    }

    div.stButton > button:first-child:hover,
    div[data-testid="stDownloadButton"] > button:first-child:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
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
        border-radius: 13px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
    }

    .section-separator {
        height: 1rem;
    }

    .section-large-spacer {
        height: 1.4rem;
    }

    .ship-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(330px, 1fr));
        gap: 1.2rem;
        margin-top: 1.1rem;
    }

    .ship-card {
        background: white;
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 24px;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
        padding: 1.35rem;
        overflow: hidden;
        min-width: 0;
    }

    .ship-card * {
        box-sizing: border-box;
        overflow-wrap: anywhere;
        min-width: 0;
    }

    .ship-header {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        margin-bottom: 1rem;
    }

    .ship-icon {
        width: 58px;
        height: 58px;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #e0f2fe;
        color: #0369a1;
        font-size: 1.75rem;
        flex: 0 0 auto;
    }

    .ship-title {
        font-size: 1.45rem;
        font-weight: 950;
        color: #111827;
        line-height: 1.08;
        margin: 0 0 0.35rem 0;
    }

    .ship-meta {
        color: #475569;
        font-size: 0.93rem;
        line-height: 1.5;
        font-weight: 650;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        margin: 0.7rem 0 1rem 0;
    }

    .chip {
        border-radius: 999px;
        padding: 0.35rem 0.68rem;
        background: #f1f5f9;
        color: #334155;
        font-size: 0.82rem;
        font-weight: 850;
        line-height: 1.2;
    }

    .chip.green {
        background: #d1fae5;
        color: #047857;
    }

    .ship-metrics {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.7rem;
        margin-top: 0.8rem;
    }

    .ship-metric {
        background: #f7f4ee;
        border-radius: 16px;
        padding: 0.85rem;
        min-height: 78px;
    }

    .ship-metric-label {
        color: #5b6472;
        font-size: 0.82rem;
        font-weight: 750;
        margin-bottom: 0.3rem;
        line-height: 1.25;
    }

    .ship-metric-value {
        color: #111827;
        font-size: 1.15rem;
        font-weight: 950;
        line-height: 1.2;
    }

    .ship-detail-box {
        margin-top: 1rem;
        border-top: 1px solid #e2e8f0;
        padding-top: 0.9rem;
        color: #1f2937;
        font-size: 0.92rem;
        line-height: 1.65;
    }

    .ship-detail-line {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        border-bottom: 1px solid #edf2f7;
        padding: 0.35rem 0;
    }

    .ship-detail-line span:first-child {
        color: #64748b;
        font-weight: 750;
    }

    .ship-detail-line span:last-child {
        color: #111827;
        font-weight: 850;
        text-align: right;
    }

    .notice-card {
        background: var(--warning-bg);
        border: 1px solid rgba(245, 158, 11, 0.55);
        border-radius: 20px;
        padding: 1rem 1.1rem;
        color: #7c3f00;
        font-weight: 750;
        line-height: 1.55;
        margin: 1rem 0;
        overflow-wrap: anywhere;
    }

    .profile-card {
        background: white;
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 24px;
        padding: 1.5rem;
        box-shadow: 0 16px 42px rgba(15, 23, 42, 0.08);
        overflow: hidden;
        min-height: 190px;
    }

    .profile-card h3 {
        margin: 0 0 0.65rem 0;
        font-size: 1.35rem;
        font-weight: 950;
        color: #111827;
        overflow-wrap: anywhere;
    }

    .profile-card p {
        margin: 0;
        color: #64748b;
        line-height: 1.6;
        overflow-wrap: anywhere;
    }

    .market-card {
        background: white;
        border-radius: 24px;
        border: 1px solid rgba(226, 232, 240, 0.9);
        padding: 1.25rem;
        box-shadow: 0 16px 42px rgba(15, 23, 42, 0.07);
        overflow: hidden;
        min-height: 190px;
    }

    .market-card h4 {
        margin: 0 0 0.5rem 0;
        color: #111827;
        font-size: 1.2rem;
        font-weight: 950;
    }

    .market-card p {
        color: #64748b;
        line-height: 1.55;
        margin: 0.35rem 0 0.9rem 0;
    }

    @media (max-width: 900px) {
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        .topbar {
            align-items: flex-start;
            gap: 0.9rem;
            flex-direction: column;
        }

        .topbar-left {
            width: 100%;
            justify-content: space-between;
        }

        .topbar-nav {
            display: none;
        }

        .main-content {
            margin-top: 8.7rem;
        }

        .user-dropdown {
            right: auto;
            left: 0;
            width: min(290px, calc(100vw - 3rem));
        }

        .ship-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Authentification, rôles et navigation
# ------------------------------------------------------------

def normalize_role(role):
    """Convertit les anciens noms de rôles vers les nouveaux."""
    if role == "client":
        return "visiteur"

    if role in ["employe", "employe_capitaine", "capitaine"]:
        return "proprietaire"

    return role or "visiteur"


def is_logged_in():
    """Vérifie si l'utilisateur a un rôle actif."""
    return st.session_state.get("authenticated", False)


def get_current_role():
    """Renvoie le rôle courant."""
    return normalize_role(st.session_state.get("role", "visiteur"))


def get_current_role_label():
    """Renvoie le libellé du rôle courant."""
    role = get_current_role()
    return ROLE_LABELS.get(role, "Utilisateur")


def get_current_username():
    """Renvoie le nom d'utilisateur courant."""
    return st.session_state.get("username", "visiteur")


def can_view_private_ship_data():
    """Les propriétaires et administrateurs voient les données internes."""
    return get_current_role() in ["proprietaire", "administrateur"]


def can_view_sql():
    """Le visiteur ne voit pas les requêtes SQL avancées."""
    return get_current_role() in ["proprietaire", "administrateur"]


def can_export_results():
    """Les propriétaires et administrateurs peuvent exporter."""
    return get_current_role() in ["proprietaire", "administrateur"]


def is_admin():
    """Vérifie si l'utilisateur est administrateur."""
    return get_current_role() == "administrateur"


def is_visitor():
    """Vérifie si l'utilisateur est un visiteur."""
    return get_current_role() == "visiteur"


def set_page(page_name):
    """Change la page courante."""
    st.session_state.current_page = page_name


def get_current_page():
    """Lit la page courante depuis l'URL ou la session."""
    query_page = st.query_params.get("page")

    if query_page:
        st.session_state.current_page = query_page

    return st.session_state.get("current_page", "dashboard")


def handle_logout_from_url():
    """Déconnecte l'utilisateur si le lien ?logout=1 est utilisé."""
    if st.query_params.get("logout") == "1":
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.role_label = None
        st.session_state.current_page = "dashboard"
        st.query_params.clear()
        st.rerun()


def reset_search_filters():
    """Remet les filtres de recherche à leur état initial."""
    for key, value in SEARCH_DEFAULTS.items():
        st.session_state[key] = value


def enter_as_visitor():
    """Entre dans l'application sans compte."""
    st.session_state.login_error = False
    st.session_state.authenticated = True
    st.session_state.username = "visiteur"
    st.session_state.role = "visiteur"
    st.session_state.role_label = "Visiteur"
    st.session_state.current_page = "dashboard"
    reset_search_filters()
    st.rerun()


def login_screen():
    """Affiche l'écran de connexion avec une image de fond et une carte à droite."""
    background_url = get_login_background_data_url()
    login_logo = logo_markup("login-logo", dark=True)

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
            min-height: clamp(620px, 82vh, 790px);
            height: clamp(620px, 82vh, 790px);
            width: 100%;
            max-width: 760px;
            margin-left: auto;
            margin-right: 0;

            border-radius: 28px;
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

        .login-logo {
            display: block;
            width: min(460px, 100%);
            max-height: 190px;
            object-fit: contain;
            margin: 0 auto 1.3rem auto;
        }

        .login-card {
            background: transparent;
            border-radius: 18px;
            padding: 0 0 1.5rem 0;
            width: 100%;
            max-width: 640px;
            margin: 0 auto 0.8rem auto;
            box-shadow: none;
            border: none;
        }

        .login-subtitle {
            color: #64748b;
            font-size: 1.06rem;
            margin-bottom: 0rem;
            text-align: center;
            font-weight: 700;
            line-height: 1.45;
        }

        div[data-testid="stForm"] label {
            color: #334155 !important;
            font-weight: 700 !important;
        }

        div[data-testid="stForm"] input {
            border-radius: 12px !important;
            background: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
            min-height: 2.75rem !important;
        }

        div[data-testid="stFormSubmitButton"] button {
            border-radius: 12px !important;
            font-weight: 850 !important;
            min-height: 2.9rem !important;
            box-shadow: 0 10px 22px rgba(14, 165, 233, 0.24);
        }

        .login-demo-box {
            margin-top: 1.2rem;
            background: rgba(241, 245, 249, 0.84);
            border: 1px solid #cbd5e1;
            border-radius: 14px;
            padding: 1rem 1.1rem;
            color: #334155;
            font-size: 0.94rem;
        }

        .login-demo-box summary {
            cursor: pointer;
            font-weight: 850;
            color: #1e293b;
        }

        .login-demo-content {
            margin-top: 0.8rem;
            line-height: 1.7;
            overflow-wrap: anywhere;
        }

        .visitor-note {
            text-align: center;
            color: #64748b;
            font-size: 0.92rem;
            line-height: 1.45;
            margin-top: 0.8rem;
            overflow-wrap: anywhere;
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
                f"""
                <div class="login-card">
                    {login_logo}
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

            login_submit = st.form_submit_button(
                "Se connecter",
                use_container_width=True,
            )

            visitor_submit = st.form_submit_button(
                "Continuer en visiteur",
                use_container_width=True,
            )

            st.markdown(
                """
                <div class="visitor-note">
                    Le mode visiteur permet de consulter les données publiques sans compte.
                </div>
                <div class="login-demo-box">
                    <details>
                        <summary>Comptes de démonstration</summary>
                        <div class="login-demo-content">
                            Propriétaire : <code>proprietaire</code> / <code>proprio123</code><br>
                            Administrateur : <code>admin</code> / <code>admin123</code>
                        </div>
                    </details>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if visitor_submit:
        enter_as_visitor()

    if login_submit:
        user = USERS.get(username.strip().lower())

        if user and password == user["password"]:
            st.session_state.login_error = False
            st.session_state.authenticated = True
            st.session_state.username = username.strip().lower()
            st.session_state.role = user["role"]
            st.session_state.role_label = user["label"]
            st.session_state.current_page = "dashboard"
            reset_search_filters()
            st.rerun()

        st.session_state.login_error = True
        st.rerun()


# ------------------------------------------------------------
# Connexion PostgreSQL et lecture CSV fallback
# ------------------------------------------------------------

def read_config():
    """Lit config.json à la racine du projet."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Fichier config.json introuvable : {CONFIG_PATH}")

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


@st.cache_data(show_spinner=False)
def database_available():
    """Vérifie si PostgreSQL est disponible."""
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
        return True, "PostgreSQL connecté"
    except Exception as error:
        return False, str(error)


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


def find_csv_file(filename):
    """Cherche un CSV dans plusieurs dossiers possibles."""
    search_dirs = [
        ROOT_DIR,
        ROOT_DIR / "02_DONNEES",
        APP_DIR,
        APP_DIR / "DATA",
        ROOT_DIR / "DATA",
        ROOT_DIR / "06_DATA",
        ROOT_DIR / "DONNEES",
        ROOT_DIR / "data",
        ROOT_DIR / "07_RAPPORT_FINAL",
    ]

    for directory in search_dirs:
        candidate = directory / filename
        if candidate.exists():
            return candidate

    # Recherche plus large dans le projet, sans sortir de ROOT_DIR.
    try:
        matches = list(ROOT_DIR.rglob(filename))
        if matches:
            return matches[0]
    except Exception:
        pass

    return None


@st.cache_data(show_spinner=False)
def load_csv_table(table_name):
    """Charge une table depuis CSV si PostgreSQL n'est pas disponible."""
    filename = CSV_FILES.get(table_name)

    if not filename:
        return pd.DataFrame()

    path = find_csv_file(filename)

    if not path:
        return pd.DataFrame()

    encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252"]

    for encoding in encodings:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()


def get_table_count(table_name):
    """Compte les lignes depuis PostgreSQL ou depuis CSV."""
    ok, _ = database_available()

    if ok:
        try:
            return int(run_query(f"SELECT COUNT(*) AS n FROM {table_name}")["n"].iloc[0])
        except Exception:
            rollback_connection()

    return len(load_csv_table(table_name))


# ------------------------------------------------------------
# Fonctions utilitaires
# ------------------------------------------------------------

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


def format_tonnage(value, suffix=""):
    """Formate une valeur de tonnage."""
    if pd.isna(value) or value == "":
        return "N/A"

    try:
        return f"{int(float(value)):,}".replace(",", " ") + suffix
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


def clean_text(value, default="N/A"):
    """Nettoie une valeur pour l'affichage HTML."""
    if pd.isna(value) or value is None or value == "":
        return default

    return escape(str(value))


def clean_number(value, default="N/A"):
    """Nettoie une valeur numérique pour l'affichage."""
    if pd.isna(value) or value is None or value == "":
        return default

    try:
        if float(value).is_integer():
            return f"{int(float(value)):,}".replace(",", " ")
        return f"{float(value):g}"
    except Exception:
        return escape(str(value))


def calculate_age(year):
    """Calcule l'âge d'un navire."""
    try:
        year_int = int(float(year))
        return max(date.today().year - year_int, 0)
    except Exception:
        return None


# ------------------------------------------------------------
# Construction des données navires
# ------------------------------------------------------------

def get_ship_dataframe_from_db():
    """Charge les navires enrichis depuis PostgreSQL."""
    return safe_query(
        """
        SELECT
            n.imo,
            n.mmsi,
            n.nom_navire,
            t.nom_type AS type_navire,
            c.nom_categorie AS categorie,
            n.annee_construction,
            p.nom_pays AS pavillon,
            p.code_iso2 AS code_pavillon,
            n.gross_tonnage AS gt,
            n.deadweight_tonnage AS dwt,
            n.longueur_m AS longueur,
            n.largeur_m AS largeur,
            n.tirant_eau_m AS tirant_eau,
            sc.nom_societe AS classification,
            co.nom_constructeur AS constructeur,
            pr.nom_proprietaire AS proprietaire,
            le.nom_port AS derniere_escale,
            le.date_arrivee AS derniere_arrivee,
            le.date_depart AS dernier_depart
        FROM navire n
        LEFT JOIN type_navire t
            ON n.id_type_navire = t.id_type_navire
        LEFT JOIN categorie_principale c
            ON t.id_categorie = c.id_categorie
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
        LEFT JOIN LATERAL (
            SELECT
                po.nom_port,
                e.date_arrivee,
                e.date_depart
            FROM escale e
            JOIN port po ON e.id_port = po.id_port
            WHERE e.imo = n.imo
            ORDER BY e.date_arrivee DESC NULLS LAST, e.id_escale DESC
            LIMIT 1
        ) le ON TRUE
        ORDER BY n.nom_navire;
        """
    )


def get_ship_dataframe_from_csv():
    """Charge les navires enrichis depuis les CSV du projet."""
    navire = load_csv_table("navire")
    type_navire = load_csv_table("type_navire")
    categorie = load_csv_table("categorie_principale")
    pavillon = load_csv_table("pavillon")
    classification = load_csv_table("societe_classification")
    constructeur = load_csv_table("constructeur")
    proprietaire = load_csv_table("proprietaire")
    propriete_navire = load_csv_table("propriete_navire")
    escale = load_csv_table("escale")
    port = load_csv_table("port")

    if navire.empty:
        return pd.DataFrame()

    df = navire.copy()

    if not type_navire.empty:
        df = df.merge(type_navire[["id_type_navire", "nom_type", "id_categorie"]], on="id_type_navire", how="left")
        df = df.rename(columns={"nom_type": "type_navire"})

    if not categorie.empty and "id_categorie" in df.columns:
        df = df.merge(categorie[["id_categorie", "nom_categorie"]], on="id_categorie", how="left")
        df = df.rename(columns={"nom_categorie": "categorie"})

    if not pavillon.empty:
        df = df.merge(pavillon[["id_pavillon", "nom_pays", "code_iso2"]], on="id_pavillon", how="left")
        df = df.rename(columns={"nom_pays": "pavillon", "code_iso2": "code_pavillon"})

    if not classification.empty:
        df = df.merge(
            classification[["id_societe_classification", "nom_societe"]],
            on="id_societe_classification",
            how="left",
        )
        df = df.rename(columns={"nom_societe": "classification"})

    if not constructeur.empty:
        df = df.merge(constructeur[["id_constructeur", "nom_constructeur"]], on="id_constructeur", how="left")
        df = df.rename(columns={"nom_constructeur": "constructeur"})

    if not propriete_navire.empty and not proprietaire.empty:
        current_prop = propriete_navire[
            propriete_navire["date_fin"].isna()
            | (propriete_navire["date_fin"].astype(str).str.strip() == "")
        ].copy()

        current_prop = current_prop.drop_duplicates(subset=["imo"], keep="last")
        current_prop = current_prop.merge(
            proprietaire[["id_proprietaire", "nom_proprietaire"]],
            on="id_proprietaire",
            how="left",
        )
        current_prop = current_prop.rename(columns={"nom_proprietaire": "proprietaire"})
        df = df.merge(current_prop[["imo", "proprietaire"]], on="imo", how="left")

    if not escale.empty and not port.empty:
        esc = escale.copy()
        esc["date_arrivee_sort"] = pd.to_datetime(esc["date_arrivee"], errors="coerce")
        esc = esc.sort_values(["imo", "date_arrivee_sort", "id_escale"], ascending=[True, False, False])
        esc = esc.drop_duplicates(subset=["imo"], keep="first")
        esc = esc.merge(port[["id_port", "nom_port"]], on="id_port", how="left")
        esc = esc.rename(
            columns={
                "nom_port": "derniere_escale",
                "date_arrivee": "derniere_arrivee",
                "date_depart": "dernier_depart",
            }
        )
        df = df.merge(
            esc[["imo", "derniere_escale", "derniere_arrivee", "dernier_depart"]],
            on="imo",
            how="left",
        )

    rename_map = {
        "gross_tonnage": "gt",
        "deadweight_tonnage": "dwt",
        "longueur_m": "longueur",
        "largeur_m": "largeur",
        "tirant_eau_m": "tirant_eau",
    }

    df = df.rename(columns=rename_map)
    return df


@st.cache_data(show_spinner=False)
def get_ship_dataframe():
    """Charge les navires depuis PostgreSQL ou CSV."""
    ok, _ = database_available()

    if ok:
        df = get_ship_dataframe_from_db()
        if not df.empty:
            return df

    return get_ship_dataframe_from_csv()


def get_filtered_ships(search_text, type_filter, pavillon_filter, class_filter):
    """Filtre les navires pour la recherche."""
    df = get_ship_dataframe()

    if df.empty:
        return df

    filtered = df.copy()

    if search_text.strip():
        pattern = search_text.strip().lower()

        mask = (
            filtered.get("nom_navire", pd.Series("", index=filtered.index)).astype(str).str.lower().str.contains(pattern, na=False)
            | filtered.get("imo", pd.Series("", index=filtered.index)).astype(str).str.lower().str.contains(pattern, na=False)
            | filtered.get("mmsi", pd.Series("", index=filtered.index)).astype(str).str.lower().str.contains(pattern, na=False)
        )
        filtered = filtered[mask]

    if type_filter != "Type de navire" and "type_navire" in filtered.columns:
        filtered = filtered[filtered["type_navire"].astype(str) == str(type_filter)]

    if pavillon_filter != "Pavillon" and "pavillon" in filtered.columns:
        filtered = filtered[filtered["pavillon"].astype(str) == str(pavillon_filter)]

    if class_filter != "Société de classification" and "classification" in filtered.columns:
        filtered = filtered[filtered["classification"].astype(str) == str(class_filter)]

    if "annee_construction" in filtered.columns:
        filtered = filtered.sort_values("annee_construction", na_position="last")

    return filtered.head(80)


def get_filter_values_from_ships():
    """Prépare les listes des filtres depuis les données navires."""
    df = get_ship_dataframe()

    def values(column, placeholder):
        if df.empty or column not in df.columns:
            return [placeholder]

        vals = df[column].dropna().astype(str).sort_values().unique().tolist()
        return [placeholder] + vals

    return (
        values("type_navire", "Type de navire"),
        values("pavillon", "Pavillon"),
        values("classification", "Société de classification"),
    )


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
        "categorie": "Catégorie",
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
        "derniere_escale": "Dernière escale",
    }

    display_df = display_df.rename(columns=rename_map)

    if role == "visiteur":
        wanted_columns = [
            "IMO",
            "Nom du navire",
            "Type",
            "Catégorie",
            "Année",
            "Pavillon",
            "Longueur",
        ]
    elif role == "proprietaire":
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
            "Dernière escale",
        ]
    else:
        wanted_columns = [
            "IMO",
            "MMSI",
            "Nom du navire",
            "Type",
            "Catégorie",
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
            "Dernière escale",
        ]

    existing_columns = [column for column in wanted_columns if column in display_df.columns]
    display_df = display_df[existing_columns]

    for col in ["Longueur", "Largeur", "Tirant d'eau"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(format_meter_value)

    return left_align_dataframe(display_df)


# ------------------------------------------------------------
# Graphiques
# ------------------------------------------------------------

def show_bar_chart_with_margins(df, x_col, y_col, height=360):
    """Affiche un graphique en barres avec des marges internes contrôlées."""
    if df.empty:
        st.info("Aucune donnée disponible pour ce graphique.")
        return

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X(
                f"{x_col}:N",
                sort="-y",
                title=None,
                axis=alt.Axis(
                    labelAngle=-55,
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


# ------------------------------------------------------------
# Requêtes SQL prédéfinies et requête admin
# ------------------------------------------------------------

def predefined_queries():
    """Requêtes SQL visibles pour les propriétaires et administrateurs."""
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
            {"name": "id_categorie", "label": "Catégorie principale", "type": "fk", "required": True, "fk_table": "categorie_principale", "fk_id": "id_categorie", "fk_label": "nom_categorie"},
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
            {"name": "taille_port", "label": "Taille du port", "type": "choice", "required": True, "choices": ["Very Small", "Small", "Medium", "Large"]},
            {"name": "type_port", "label": "Type de port", "type": "choice", "required": True, "choices": ["Coastal Breakwater", "Coastal Natural", "Coastal Tide Gate", "Lake or Canal", "Open Roadstead", "River Basin", "River Natural", "River Tide Gate"]},
            {"name": "capacite_max_navire", "label": "Capacité max navire", "type": "choice", "required": True, "choices": ["Over 500'", "Under 500'"]},
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
            {"name": "id_type_navire", "label": "Type de navire", "type": "fk", "required": True, "fk_table": "type_navire", "fk_id": "id_type_navire", "fk_label": "nom_type"},
            {"name": "id_pavillon", "label": "Pavillon", "type": "fk", "required": True, "fk_table": "pavillon", "fk_id": "id_pavillon", "fk_label": "nom_pays"},
            {"name": "annee_construction", "label": "Année de construction", "type": "int", "required": True},
            {"name": "gross_tonnage", "label": "Gross tonnage", "type": "int", "required": True},
            {"name": "deadweight_tonnage", "label": "Deadweight tonnage", "type": "int", "required": True},
            {"name": "longueur_m", "label": "Longueur en m", "type": "numeric", "required": True},
            {"name": "largeur_m", "label": "Largeur en m", "type": "numeric", "required": True},
            {"name": "tirant_eau_m", "label": "Tirant d'eau en m", "type": "numeric", "required": True},
            {"name": "id_societe_classification", "label": "Société de classification", "type": "fk", "required": True, "fk_table": "societe_classification", "fk_id": "id_societe_classification", "fk_label": "nom_societe"},
            {"name": "id_constructeur", "label": "Constructeur", "type": "fk", "required": True, "fk_table": "constructeur", "fk_id": "id_constructeur", "fk_label": "nom_constructeur"},
        ],
    },
    "propriete_navire": {
        "label": "Propriétés des navires",
        "primary_key": ["imo", "id_proprietaire", "date_debut"],
        "display_columns": ["imo", "id_proprietaire", "date_debut"],
        "fields": [
            {"name": "imo", "label": "Navire", "type": "fk", "required": True, "fk_table": "navire", "fk_id": "imo", "fk_label": "nom_navire"},
            {"name": "id_proprietaire", "label": "Propriétaire", "type": "fk", "required": True, "fk_table": "proprietaire", "fk_id": "id_proprietaire", "fk_label": "nom_proprietaire"},
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
            {"name": "imo", "label": "Navire", "type": "fk", "required": True, "fk_table": "navire", "fk_id": "imo", "fk_label": "nom_navire"},
            {"name": "id_port", "label": "Port", "type": "fk", "required": True, "fk_table": "port", "fk_id": "id_port", "fk_label": "nom_port"},
            {"name": "date_arrivee", "label": "Date d'arrivée", "type": "date", "required": True},
            {"name": "heure_arrivee", "label": "Heure d'arrivée", "type": "time", "required": False},
            {"name": "date_depart", "label": "Date de départ", "type": "date", "required": False},
            {"name": "heure_depart", "label": "Heure de départ", "type": "time", "required": False},
        ],
    },
}


def get_next_id(table_name, column_name):
    """Propose l'identifiant suivant pour les tables sans séquence SQL."""
    ok, _ = database_available()

    if ok:
        df = safe_query(f"SELECT COALESCE(MAX({column_name}), 0) + 1 AS next_id FROM {table_name};")
        if not df.empty:
            return int(df["next_id"].iloc[0])

    csv_df = load_csv_table(table_name)
    if csv_df.empty or column_name not in csv_df.columns:
        return 1

    return int(pd.to_numeric(csv_df[column_name], errors="coerce").max()) + 1


def get_fk_options(field):
    """Récupère les valeurs possibles pour une clé étrangère."""
    table_name = field["fk_table"]
    id_column = field["fk_id"]
    label_column = field["fk_label"]
    ok, _ = database_available()

    if ok:
        df = safe_query(
            f"""
            SELECT {id_column} AS id_value, {label_column} AS label_value
            FROM {table_name}
            ORDER BY {label_column};
            """
        )
    else:
        raw_df = load_csv_table(table_name)
        if raw_df.empty or id_column not in raw_df.columns or label_column not in raw_df.columns:
            df = pd.DataFrame()
        else:
            df = raw_df[[id_column, label_column]].copy()
            df = df.rename(columns={id_column: "id_value", label_column: "label_value"})
            df = df.sort_values("label_value")

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
    ok, _ = database_available()

    if ok:
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

    raw_df = load_csv_table(table_name)
    if raw_df.empty:
        return pd.DataFrame()

    cols = [col for col in config["display_columns"] if col in raw_df.columns]
    if not cols:
        return pd.DataFrame()

    return raw_df[cols].head(300)


def get_full_row(table_name, config, selected_row):
    """Charge toutes les colonnes d'une ligne sélectionnée."""
    ok, _ = database_available()

    if ok:
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

    raw_df = load_csv_table(table_name)
    if raw_df.empty:
        return pd.DataFrame()

    mask = pd.Series(True, index=raw_df.index)

    for pk_column in config["primary_key"]:
        mask = mask & (raw_df[pk_column].astype(str) == str(selected_row[pk_column]))

    return raw_df[mask].head(1)


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
    ok, _ = database_available()

    if not ok:
        raise RuntimeError(
            "PostgreSQL n'est pas connecté. Le mode CSV permet la consultation, "
            "mais pas l'écriture directe dans les fichiers."
        )

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
    ok, _ = database_available()

    if not ok:
        raise RuntimeError(
            "PostgreSQL n'est pas connecté. Le mode CSV permet la consultation, "
            "mais pas l'écriture directe dans les fichiers."
        )

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


# ------------------------------------------------------------
# Rendu des composants
# ------------------------------------------------------------

def render_topbar():
    """Affiche la barre de navigation avec menu utilisateur."""
    role_label = get_current_role_label()
    username = get_current_username()
    logo = logo_markup("topbar-logo", dark=False)

    auth_label = "Se connecter" if is_visitor() else "Se déconnecter"
    auth_href = "?logout=1"

    menu_html = f'''
<div class="topbar">
    <div class="topbar-left">
        <a href="?page=dashboard" target="_self">{logo}</a>
        <div class="topbar-nav">
            <a href="?page=dashboard" target="_self">Accueil</a>
            <a href="?page=ships" target="_self">Bateaux</a>
            <a href="?page=owner_request" target="_self">Devenir propriétaire</a>
        </div>
    </div>
    <details class="user-menu">
        <summary>{escape(role_label)} <span class="chevron">⌄</span></summary>
        <div class="user-dropdown">
            <div class="account-line">
                <strong>{escape(role_label)}</strong>
                <span>Compte actuel : {escape(username)}</span>
            </div>
            <a href="?page=profile" target="_self">Profil</a>
            <a href="?page=settings" target="_self">Paramètres</a>
            <a href="?page=ships" target="_self">Voir tous les bateaux</a>
            <a href="?page=owner_request" target="_self">Devenir propriétaire</a>
            <a href="{auth_href}" target="_self">{auth_label}</a>
        </div>
    </details>
</div>
'''
    render_html(menu_html)

def render_hero(title, subtitle):
    """Affiche un hero moderne."""
    render_html(
        f'''
<div class="hero-panel">
    <div class="hero-title">{escape(title)}</div>
    <p class="hero-subtitle">{escape(subtitle)}</p>
</div>
'''
    )


def render_metric_card(label, value, note):
    """Affiche une métrique."""
    render_html(
        f'''
<div class="metric-card">
    <div class="metric-label">{escape(label)}</div>
    <div class="metric-value">{escape(str(value))}</div>
    <div class="metric-note">{escape(note)}</div>
</div>
'''
    )

def render_ship_cards(df, detailed=False, limit=24):
    """Affiche les navires sous forme de cartes modernes."""
    if df.empty:
        st.info("Aucun navire disponible.")
        return

    cards = ['<div class="ship-grid">']

    for _, row in df.head(limit).iterrows():
        name = escape(clean_text(row.get("nom_navire")))
        imo = escape(clean_number(row.get("imo")))
        mmsi = escape(clean_number(row.get("mmsi")))
        ship_type = escape(clean_text(row.get("type_navire")))
        category = escape(clean_text(row.get("categorie")))
        pavillon = escape(clean_text(row.get("pavillon")))
        year = escape(clean_number(row.get("annee_construction")))
        age = calculate_age(row.get("annee_construction"))
        age_text = escape(f"{age} ans" if age is not None else "Âge N/A")
        gt = escape(format_tonnage(row.get("gt")))
        dwt = escape(format_tonnage(row.get("dwt"), " t"))
        length = escape(f"{clean_number(row.get('longueur'))} m")
        width = escape(f"{clean_number(row.get('largeur'))} m")
        draft = escape(f"{clean_number(row.get('tirant_eau'))} m")
        classification = escape(clean_text(row.get("classification")))
        constructeur = escape(clean_text(row.get("constructeur")))
        proprietaire = escape(clean_text(row.get("proprietaire"), "Non renseigné"))
        last_port = escape(clean_text(row.get("derniere_escale"), "Aucune escale connue"))
        last_arrival = escape(clean_text(row.get("derniere_arrivee"), "N/A"))
        last_depart = row.get("dernier_depart")
        status = escape("En port" if pd.isna(last_depart) or str(last_depart).strip() == "" else "Terminé")

        private_details = ""
        if detailed:
            private_details = dedent(
                f'''
                <div class="ship-detail-box">
                    <div class="ship-detail-line"><span>Constructeur</span><span>{constructeur}</span></div>
                    <div class="ship-detail-line"><span>Classification</span><span>{classification}</span></div>
                    <div class="ship-detail-line"><span>Propriétaire actuel</span><span>{proprietaire}</span></div>
                    <div class="ship-detail-line"><span>Dernière escale</span><span>{last_port}</span></div>
                    <div class="ship-detail-line"><span>Arrivée</span><span>{last_arrival}</span></div>
                    <div class="ship-detail-line"><span>Statut trajet</span><span>{status}</span></div>
                </div>
                '''
            ).strip()

        cards.append(
            dedent(
                f'''
                <div class="ship-card">
                    <div class="ship-header">
                        <div class="ship-icon">⚓</div>
                        <div class="ship-heading-text">
                            <div class="ship-title">{name}</div>
                            <div class="ship-meta">IMO {imo} · MMSI {mmsi}</div>
                        </div>
                    </div>
                    <div class="chip-row">
                        <span class="chip green">{pavillon}</span>
                        <span class="chip">{ship_type}</span>
                        <span class="chip">{category}</span>
                        <span class="chip">{age_text}</span>
                    </div>
                    <div class="ship-metrics">
                        <div class="ship-metric"><div class="ship-metric-label">Jauge brute (GT)</div><div class="ship-metric-value">{gt}</div></div>
                        <div class="ship-metric"><div class="ship-metric-label">Port en lourd (DWT)</div><div class="ship-metric-value">{dwt}</div></div>
                        <div class="ship-metric"><div class="ship-metric-label">Longueur</div><div class="ship-metric-value">{length}</div></div>
                        <div class="ship-metric"><div class="ship-metric-label">Largeur</div><div class="ship-metric-value">{width}</div></div>
                    </div>
                    <div class="ship-detail-box">
                        <div class="ship-detail-line"><span>Année</span><span>{year}</span></div>
                        <div class="ship-detail-line"><span>Tirant d'eau</span><span>{draft}</span></div>
                    </div>
                    {private_details}
                </div>
                '''
            ).strip()
        )

    cards.append("</div>")
    render_html("\n".join(cards))

    if len(df) > limit:
        st.caption(f"{limit} navires affichés sur {len(df)}. Utilise la recherche ou les filtres pour affiner.")


# ------------------------------------------------------------
# Pages
# ------------------------------------------------------------

def show_dashboard():
    """Page principale."""
    render_hero(
        "Tableau de bord maritime",
        "Consulte les données publiques des navires et explore les informations détaillées selon ton rôle.",
    )

    ok, db_message = database_available()

    if not ok:
        st.markdown(
            """
            <div class="notice-card">
                Mode consultation CSV activé : PostgreSQL n'est pas connecté.
                Les cartes, recherches et statistiques utilisent les fichiers CSV disponibles dans le projet.
                Les modifications directes de la base restent réservées au mode PostgreSQL.
            </div>
            """,
            unsafe_allow_html=True,
        )

    ships = get_ship_dataframe()

    navire_count = len(ships)
    pavillon_count = ships["pavillon"].dropna().nunique() if "pavillon" in ships.columns else get_table_count("pavillon")
    port_count = get_table_count("port")
    classification_count = ships["classification"].dropna().nunique() if "classification" in ships.columns else get_table_count("societe_classification")

    m1, m2, m3, m4 = st.columns([1, 1, 1, 1], gap="medium")

    with m1:
        render_metric_card("Navires enregistrés", f"{navire_count:,}".replace(",", " "), "données IMO")

    with m2:
        render_metric_card("Pavillons représentés", f"{pavillon_count:,}".replace(",", " "), "pays différents")

    with m3:
        render_metric_card("Ports suivis", f"{port_count:,}".replace(",", " "), "escales possibles")

    with m4:
        render_metric_card("Source active", "PostgreSQL" if ok else "CSV", "mode de données")

    show_search_and_results(ships)
    show_stats(ships)

    if can_view_sql():
        show_predefined_sql_section()

    if is_admin():
        show_custom_admin_sql()
        show_admin_data_management_panel()


def show_search_and_results(ships):
    """Recherche multicritère."""
    st.markdown(
        """
        <div class="search-header-box">
            <div class="section-title">Recherche multicritère</div>
            <div class="section-help">
                Les informations affichées changent selon le rôle connecté.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    type_values, pavillon_values, classification_values = get_filter_values_from_ships()
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

    results = get_filtered_ships(
        search_text,
        selected_type,
        selected_pavillon,
        selected_classification,
    )

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

    st.markdown(
        """
        <div class="results-header-box">
            <div class="section-title">Résultats de recherche</div>
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


def show_stats(ships):
    """Statistiques rapides."""
    st.markdown(
        """
        <div class="stats-header-box">
            <div class="section-title">Statistiques rapides</div>
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

        if ships.empty or "type_navire" not in ships.columns:
            chart_df = pd.DataFrame()
        else:
            chart_df = (
                ships.groupby("type_navire", dropna=True)
                .size()
                .reset_index(name="nombre_navires")
                .sort_values("nombre_navires", ascending=False)
                .head(10)
            )

        show_bar_chart_with_margins(chart_df, "type_navire", "nombre_navires")

    with chart_col2:
        st.markdown(
            '<div class="chart-title">Top pavillons</div>',
            unsafe_allow_html=True,
        )

        if ships.empty or "pavillon" not in ships.columns:
            chart_df = pd.DataFrame()
        else:
            chart_df = (
                ships.groupby("pavillon", dropna=True)
                .size()
                .reset_index(name="nombre_navires")
                .sort_values("nombre_navires", ascending=False)
                .head(10)
            )

        show_bar_chart_with_margins(chart_df, "pavillon", "nombre_navires")

    if can_view_private_ship_data():
        st.markdown('<div class="chart-row-spacer"></div>', unsafe_allow_html=True)

        chart_col3, chart_col4 = st.columns([1, 1], gap="medium")

        with chart_col3:
            st.markdown(
                '<div class="chart-title">Constructeurs les plus représentés</div>',
                unsafe_allow_html=True,
            )

            if ships.empty or "constructeur" not in ships.columns:
                chart_df = pd.DataFrame()
            else:
                chart_df = (
                    ships.groupby("constructeur", dropna=True)
                    .size()
                    .reset_index(name="nombre_navires")
                    .sort_values("nombre_navires", ascending=False)
                    .head(10)
                )

            show_bar_chart_with_margins(chart_df, "constructeur", "nombre_navires")

        with chart_col4:
            st.markdown(
                "<div class=\"chart-title\">Ports avec le plus d'escales</div>",
                unsafe_allow_html=True,
            )

            escales = load_csv_table("escale")
            ports = load_csv_table("port")

            if not escales.empty and not ports.empty:
                chart_df = (
                    escales.merge(ports[["id_port", "nom_port"]], on="id_port", how="left")
                    .groupby("nom_port", dropna=True)
                    .size()
                    .reset_index(name="nombre_escales")
                    .rename(columns={"nom_port": "port"})
                    .sort_values("nombre_escales", ascending=False)
                    .head(10)
                )
            else:
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


def show_all_ships_page():
    """Page Voir tous les bateaux."""
    render_hero(
        "Tous les bateaux",
        "Explore les navires sous forme de cartes. Les visiteurs voient les informations publiques, les propriétaires et administrateurs voient les informations détaillées.",
    )

    ships = get_ship_dataframe()

    type_values, pavillon_values, classification_values = get_filter_values_from_ships()

    f1, f2, f3 = st.columns([2, 1, 1], gap="medium")

    with f1:
        card_search = st.text_input(
            "Rechercher un bateau",
            placeholder="Nom, IMO ou MMSI...",
            key="ship_cards_search",
        )

    with f2:
        card_type = st.selectbox(
            "Type",
            type_values,
            key="ship_cards_type",
        )

    with f3:
        card_pavillon = st.selectbox(
            "Pavillon",
            pavillon_values,
            key="ship_cards_pavillon",
        )

    filtered = get_filtered_ships(
        card_search,
        card_type,
        card_pavillon,
        "Société de classification",
    )

    render_ship_cards(
        filtered,
        detailed=can_view_private_ship_data(),
        limit=36,
    )


def show_profile_page():
    """Page Profil."""
    render_hero(
        "Profil",
        "Consulte ton rôle actuel et les accès disponibles dans l'interface ShipData.",
    )

    c1, c2, c3 = st.columns([1, 1, 1], gap="medium")

    with c1:
        st.markdown(
            f"""
            <div class="profile-card">
                <h3>Compte actuel</h3>
                <p><strong>Utilisateur :</strong> {escape(get_current_username())}</p>
                <p><strong>Rôle :</strong> {escape(get_current_role_label())}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        if is_visitor():
            access_text = "Accès public : recherche, statistiques publiques et cartes simplifiées des bateaux."
        elif get_current_role() == "proprietaire":
            access_text = "Accès propriétaire : détails des navires, constructeur, classification, escales et exports."
        else:
            access_text = "Accès administrateur : toutes les données, requêtes SQL et gestion des informations."

        st.markdown(
            f"""
            <div class="profile-card">
                <h3>Droits du profil</h3>
                <p>{escape(access_text)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="profile-card">
                <h3>Mode démonstration</h3>
                <p>{escape(DEMO_OWNER_TEXT)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if get_current_role() == "proprietaire":
        st.markdown(
            f"""
            <div class="notice-card">
                Propriétaire démo : {escape(DEMO_OWNER_NAME)} · Navire rattaché : {escape(DEMO_OWNER_SHIP)}.
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_settings_page():
    """Page Paramètres."""
    render_hero(
        "Paramètres",
        "Options de consultation et informations techniques du projet.",
    )

    ok, message = database_available()
    data_source = "PostgreSQL" if ok else "CSV fallback"

    c1, c2 = st.columns([1, 1], gap="medium")

    with c1:
        st.markdown(
            f"""
            <div class="profile-card">
                <h3>Source des données</h3>
                <p><strong>Mode actuel :</strong> {escape(data_source)}</p>
                <p>Si PostgreSQL n'est pas disponible, l'interface utilise les CSV du projet pour rester consultable.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="profile-card">
                <h3>Confidentialité des rôles</h3>
                <p>Les visiteurs voient les informations publiques. Les propriétaires et administrateurs voient les données internes utiles à la gestion maritime.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not ok:
        with st.expander("Détail de la connexion PostgreSQL"):
            st.write(message)


def show_owner_request_page():
    """Page Devenir propriétaire."""
    render_hero(
        "Devenir propriétaire",
        "Déclare un bateau existant, mets à jour tes informations, ou explore l'achat d'un nouveau navire.",
    )

    st.markdown(
        """
        <div class="notice-card">
            Dans cette version, le formulaire crée une demande de démonstration.
            Une validation réelle par les administrateurs pourra être ajoutée ensuite.
        </div>
        """,
        unsafe_allow_html=True,
    )

    request_tab, buy_tab = st.tabs(["Déclarer ou mettre à jour un bateau", "Acheter un nouveau bateau"])

    with request_tab:
        with st.form("owner_request_form"):
            st.subheader("Demande propriétaire")

            col1, col2 = st.columns([1, 1], gap="medium")

            with col1:
                owner_name = st.text_input("Nom ou société propriétaire")
                contact_email = st.text_input("Adresse email")
                ship_name = st.text_input("Nom du bateau")
                imo = st.text_input("IMO du bateau")

            with col2:
                pavillon = st.text_input("Pavillon")
                ship_type = st.text_input("Type de navire")
                proof_text = st.text_area(
                    "Informations justificatives",
                    placeholder="Contrat, preuve de propriété, informations d'immatriculation...",
                    height=140,
                )

            submitted = st.form_submit_button("Envoyer la demande aux admins", use_container_width=True)

        if submitted:
            if not owner_name.strip() or not ship_name.strip():
                st.warning("Remplis au minimum le nom du propriétaire et le nom du bateau.")
            else:
                st.session_state.setdefault("owner_requests", []).append(
                    {
                        "owner_name": owner_name,
                        "contact_email": contact_email,
                        "ship_name": ship_name,
                        "imo": imo,
                        "pavillon": pavillon,
                        "ship_type": ship_type,
                        "proof_text": proof_text,
                    }
                )
                st.success("Demande envoyée en mode démonstration. Elle devra être validée par un administrateur.")

    with buy_tab:
        st.markdown(
            """
            <div class="ship-grid">
                <div class="market-card">
                    <h4>Cargo polyvalent</h4>
                    <p>Pour les routes commerciales régionales, avec une capacité flexible pour marchandises générales.</p>
                    <div class="chip-row">
                        <span class="chip green">Disponible</span>
                        <span class="chip">Cargo sec</span>
                    </div>
                </div>
                <div class="market-card">
                    <h4>Porte-conteneurs léger</h4>
                    <p>Option adaptée aux lignes régulières et au transport de conteneurs sur moyenne distance.</p>
                    <div class="chip-row">
                        <span class="chip green">Sur demande</span>
                        <span class="chip">Conteneurs</span>
                    </div>
                </div>
                <div class="market-card">
                    <h4>Navire de service portuaire</h4>
                    <p>Solution plus compacte pour opérations de soutien, manœuvres et services locaux.</p>
                    <div class="chip-row">
                        <span class="chip green">Nouveau</span>
                        <span class="chip">Service</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Contacter ShipData pour un achat", use_container_width=True):
            st.success("Demande d'achat enregistrée en mode démonstration.")


def show_predefined_sql_section():
    """Section des requêtes SQL prédéfinies."""
    ok, _ = database_available()

    if not ok:
        st.info("Les requêtes SQL prédéfinies nécessitent une connexion PostgreSQL active.")
        return

    queries = predefined_queries()
    query_titles = list(queries.keys())

    st.markdown('<div class="section-separator"></div>', unsafe_allow_html=True)
    left, right = st.columns([1, 1], gap="medium")

    with left:
        st.markdown(
            '<div class="panel"><div class="section-title">Requêtes SQL disponibles</div>',
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
            '<div class="panel"><div class="section-title">Aperçu SQL</div>',
            unsafe_allow_html=True,
        )

        selected_sql = queries.get(st.session_state.get("selected_query"), "")
        st.markdown(f'<div class="sql-box">{escape(selected_sql)}</div>', unsafe_allow_html=True)

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


def show_custom_admin_sql():
    """Requête personnalisée réservée à l'administrateur."""
    ok, _ = database_available()

    st.markdown(
        '<div class="panel"><div class="section-title">Requête SELECT personnalisée</div>',
        unsafe_allow_html=True,
    )

    if not ok:
        st.info("La requête SQL personnalisée nécessite PostgreSQL.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

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


def show_admin_data_management_panel():
    """Affiche la section admin dans une carte."""
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    show_admin_data_management()
    st.markdown("</div>", unsafe_allow_html=True)


def show_admin_data_management():
    """Affiche la section admin pour ajouter ou modifier les données."""
    st.markdown(
        """
        <div class="section-title">Gestion des données</div>
        <div class="section-help">
            Cette section est réservée à l'administrateur. Elle permet d'ajouter de nouvelles lignes
            ou de modifier des lignes existantes. Les écritures nécessitent PostgreSQL.
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
                    get_ship_dataframe.clear()
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
                            get_ship_dataframe.clear()
                        except Exception as error:
                            st.error("Impossible de modifier cette donnée.")
                            st.exception(error)


# ------------------------------------------------------------
# Démarrage de l'application
# ------------------------------------------------------------

handle_logout_from_url()

if not is_logged_in():
    login_screen()
    st.stop()

render_topbar()
st.markdown('<div class="main-content">', unsafe_allow_html=True)

current_page = get_current_page()

if current_page == "profile":
    show_profile_page()
elif current_page == "settings":
    show_settings_page()
elif current_page == "ships":
    show_all_ships_page()
elif current_page == "owner_request":
    show_owner_request_page()
else:
    show_dashboard()

st.markdown(
    """
    <div style="text-align:center;color:#94a3b8;font-size:0.85rem;margin-top:2.8rem;">
        Projet de bases de données — ShipData — Interface Streamlit avec rôles utilisateur
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
