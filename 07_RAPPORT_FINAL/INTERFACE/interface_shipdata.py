# Interface Streamlit pour le projet ShipData
# Projet BD - Printemps 2026
# Le code est volontairement simple et commenté pour rester compréhensible.

import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
import psycopg2
import streamlit as st


CONFIG_PATH = Path("config.json")


# -----------------------------
# Fonctions utilitaires
# -----------------------------

def normalize(text):
    """Je simplifie un nom pour comparer les colonnes plus facilement."""
    if text is None:
        return ""
    text = str(text).lower()
    text = text.replace("é", "e").replace("è", "e").replace("ê", "e")
    text = text.replace("à", "a").replace("â", "a")
    text = text.replace("î", "i").replace("ï", "i")
    text = text.replace("ô", "o")
    text = text.replace("ù", "u").replace("û", "u")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def quote_ident(name):
    """Je protège les noms de tables/colonnes pour PostgreSQL."""
    return '"' + str(name).replace('"', '""') + '"'


@st.cache_data
def load_config():
    """Je lis le fichier config.json. Si le fichier n'existe pas, je propose des valeurs par défaut."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    return {
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": "",
        "database": "shipdata",
    }


@st.cache_resource
def get_connection(config):
    """Je crée la connexion à PostgreSQL."""
    return psycopg2.connect(
        host=config.get("host", "localhost"),
        port=config.get("port", 5432),
        user=config.get("user", "postgres"),
        password=config.get("password", ""),
        dbname=config.get("database", "shipdata"),
    )


def run_query(sql, params=None):
    """Je lance une requête SELECT et je récupère le résultat dans un DataFrame."""
    conn = get_connection(load_config())
    return pd.read_sql_query(sql, conn, params=params)


@st.cache_data
def get_tables():
    """Je récupère les tables visibles de la base."""
    sql = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name;
    """
    return run_query(sql)


@st.cache_data
def get_columns():
    """Je récupère toutes les colonnes des tables visibles."""
    sql = """
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name, ordinal_position;
    """
    return run_query(sql)


def find_table(table_keywords):
    """Je cherche une table dont le nom correspond à un mot-clé."""
    tables = get_tables()
    for _, row in tables.iterrows():
        full_name = f"{row['table_schema']}.{row['table_name']}"
        simple_name = normalize(row["table_name"])
        for keyword in table_keywords:
            if normalize(keyword) in simple_name:
                return row["table_schema"], row["table_name"], full_name
    return None


def get_table_columns(schema, table):
    """Je récupère les colonnes d'une table donnée."""
    columns = get_columns()
    selected = columns[(columns["table_schema"] == schema) & (columns["table_name"] == table)]
    return list(selected["column_name"])


def find_column(columns, keywords):
    """Je cherche une colonne qui contient un des mots-clés donnés."""
    normalized = {column: normalize(column) for column in columns}
    for keyword in keywords:
        key = normalize(keyword)
        for column, simple_column in normalized.items():
            if key == simple_column or key in simple_column:
                return column
    return None


def detect_ship_context():
    """Je détecte automatiquement la table principale des navires et ses colonnes utiles."""
    result = find_table(["navire", "vessel", "ship", "bateau"])
    if result is None:
        return None

    schema, table, full_name = result
    columns = get_table_columns(schema, table)

    return {
        "schema": schema,
        "table": table,
        "full_name": full_name,
        "columns": columns,
        "imo": find_column(columns, ["imo", "numero_imo", "num_imo"]),
        "name": find_column(columns, ["nom", "name", "vessel_name", "ship_name", "navire"]),
        "type": find_column(columns, ["type", "type_navire", "ship_type", "vessel_type"]),
        "year": find_column(columns, ["annee", "annee_construction", "construction", "year", "built"]),
        "tonnage": find_column(columns, ["tonnage", "gross", "gt", "jauge"]),
        "length": find_column(columns, ["longueur", "length"]),
        "width": find_column(columns, ["largeur", "width", "beam"]),
        "draft": find_column(columns, ["tirant", "draft", "draught"]),
        "flag": find_column(columns, ["pavillon", "flag", "pays"]),
        "classification": find_column(columns, ["classification", "societe_classification", "class"]),
        "builder": find_column(columns, ["constructeur", "builder", "chantier"]),
        "owner": find_column(columns, ["proprietaire", "owner"]),
        "manager": find_column(columns, ["gestionnaire", "manager"]),
    }


def select_columns(context):
    """Je choisis les colonnes principales à afficher dans le tableau des navires."""
    wanted = [
        context.get("imo"),
        context.get("name"),
        context.get("type"),
        context.get("year"),
        context.get("flag"),
        context.get("tonnage"),
        context.get("classification"),
        context.get("builder"),
        context.get("owner"),
        context.get("manager"),
    ]
    selected = [column for column in wanted if column is not None]
    return selected if selected else context["columns"][:10]


def build_filter_query(context, search_text, selected_type, selected_flag):
    """Je construis une requête simple avec les filtres de l'interface."""
    table_name = quote_ident(context["schema"]) + "." + quote_ident(context["table"])
    display_columns = select_columns(context)
    sql = "SELECT " + ", ".join(quote_ident(col) for col in display_columns)
    sql += f" FROM {table_name} WHERE 1=1"
    params = []

    if search_text:
        search_parts = []
        if context.get("name"):
            search_parts.append(f"CAST({quote_ident(context['name'])} AS TEXT) ILIKE %s")
            params.append(f"%{search_text}%")
        if context.get("imo"):
            search_parts.append(f"CAST({quote_ident(context['imo'])} AS TEXT) ILIKE %s")
            params.append(f"%{search_text}%")
        if search_parts:
            sql += " AND (" + " OR ".join(search_parts) + ")"

    if selected_type != "Tous" and context.get("type"):
        sql += f" AND CAST({quote_ident(context['type'])} AS TEXT) = %s"
        params.append(selected_type)

    if selected_flag != "Tous" and context.get("flag"):
        sql += f" AND CAST({quote_ident(context['flag'])} AS TEXT) = %s"
        params.append(selected_flag)

    if context.get("name"):
        sql += f" ORDER BY {quote_ident(context['name'])}"

    sql += " LIMIT 500;"
    return sql, params


def get_distinct_values(context, column):
    """Je récupère les valeurs distinctes d'une colonne pour les menus de filtre."""
    if column is None:
        return ["Tous"]
    table_name = quote_ident(context["schema"]) + "." + quote_ident(context["table"])
    sql = f"""
        SELECT DISTINCT CAST({quote_ident(column)} AS TEXT) AS value
        FROM {table_name}
        WHERE {quote_ident(column)} IS NOT NULL
        ORDER BY value
        LIMIT 200;
    """
    values = run_query(sql)["value"].dropna().astype(str).tolist()
    return ["Tous"] + values


def metric_count(context):
    table_name = quote_ident(context["schema"]) + "." + quote_ident(context["table"])
    return int(run_query(f"SELECT COUNT(*) AS total FROM {table_name};")["total"].iloc[0])


def metric_average(context, column):
    if column is None:
        return None
    table_name = quote_ident(context["schema"]) + "." + quote_ident(context["table"])
    sql = f"SELECT AVG(CAST({quote_ident(column)} AS NUMERIC)) AS average_value FROM {table_name};"
    try:
        value = run_query(sql)["average_value"].iloc[0]
        return None if pd.isna(value) else float(value)
    except Exception:
        return None


def group_count(context, column, limit=10):
    """Je compte les navires par catégorie."""
    if column is None:
        return pd.DataFrame()
    table_name = quote_ident(context["schema"]) + "." + quote_ident(context["table"])
    sql = f"""
        SELECT CAST({quote_ident(column)} AS TEXT) AS categorie, COUNT(*) AS nombre
        FROM {table_name}
        WHERE {quote_ident(column)} IS NOT NULL
        GROUP BY CAST({quote_ident(column)} AS TEXT)
        ORDER BY nombre DESC, categorie
        LIMIT {int(limit)};
    """
    return run_query(sql)


def predefined_queries(context):
    """Je prépare des requêtes prédéfinies selon les colonnes trouvées."""
    table_name = quote_ident(context["schema"]) + "." + quote_ident(context["table"])
    queries = {}

    queries["Tous les navires"] = f"SELECT * FROM {table_name} LIMIT 100;"

    if context.get("year"):
        year_col = quote_ident(context["year"])
        current_year = date.today().year
        queries["Navires construits avant 1995"] = f"""
SELECT *
FROM {table_name}
WHERE CAST({year_col} AS INTEGER) < 1995
ORDER BY {year_col}
LIMIT 100;
"""
        queries["Navires de plus de 30 ans"] = f"""
SELECT *, ({current_year} - CAST({year_col} AS INTEGER)) AS age
FROM {table_name}
WHERE ({current_year} - CAST({year_col} AS INTEGER)) > 30
ORDER BY age DESC
LIMIT 100;
"""

    if context.get("tonnage"):
        tonnage_col = quote_ident(context["tonnage"])
        queries["Navires ayant le plus grand tonnage"] = f"""
SELECT *
FROM {table_name}
WHERE {tonnage_col} IS NOT NULL
ORDER BY CAST({tonnage_col} AS NUMERIC) DESC
LIMIT 20;
"""

    if context.get("type") and context.get("year"):
        type_col = quote_ident(context["type"])
        year_col = quote_ident(context["year"])
        current_year = date.today().year
        queries["Âge moyen des navires par type"] = f"""
SELECT CAST({type_col} AS TEXT) AS type_navire,
       ROUND(AVG({current_year} - CAST({year_col} AS INTEGER)), 2) AS age_moyen,
       COUNT(*) AS nombre_navires
FROM {table_name}
WHERE {type_col} IS NOT NULL AND {year_col} IS NOT NULL
GROUP BY CAST({type_col} AS TEXT)
ORDER BY age_moyen DESC;
"""

    if context.get("flag") and context.get("tonnage"):
        flag_col = quote_ident(context["flag"])
        tonnage_col = quote_ident(context["tonnage"])
        queries["Tonnage moyen selon le pavillon"] = f"""
SELECT CAST({flag_col} AS TEXT) AS pavillon,
       ROUND(AVG(CAST({tonnage_col} AS NUMERIC)), 2) AS tonnage_moyen,
       COUNT(*) AS nombre_navires
FROM {table_name}
WHERE {flag_col} IS NOT NULL AND {tonnage_col} IS NOT NULL
GROUP BY CAST({flag_col} AS TEXT)
ORDER BY tonnage_moyen DESC;
"""

    for label, key in [
        ("Nombre de navires par type", "type"),
        ("Pavillons les plus fréquents", "flag"),
        ("Constructeurs les plus représentés", "builder"),
        ("Propriétaires avec le plus de navires", "owner"),
        ("Sociétés de classification les plus présentes", "classification"),
        ("Gestionnaires avec le plus de navires", "manager"),
    ]:
        column = context.get(key)
        if column:
            col = quote_ident(column)
            queries[label] = f"""
SELECT CAST({col} AS TEXT) AS categorie, COUNT(*) AS nombre_navires
FROM {table_name}
WHERE {col} IS NOT NULL
GROUP BY CAST({col} AS TEXT)
ORDER BY nombre_navires DESC
LIMIT 20;
"""

    return queries


def safe_custom_query(sql):
    """Je bloque les requêtes dangereuses dans l'interface libre."""
    cleaned = sql.strip().lower()
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate", "create", "grant", "revoke"]
    if not cleaned.startswith("select"):
        return False
    return not any(word in cleaned for word in forbidden)


# -----------------------------
# Interface Streamlit
# -----------------------------

st.set_page_config(
    page_title="ShipData",
    page_icon="🚢",
    layout="wide",
)

st.title("🚢 ShipData")
st.caption("Structure et analyse des flottes maritimes — projet de base de données")

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Choisir une page",
        ["Accueil", "Explorer les navires", "Analyses", "Requêtes SQL", "Structure de la base"],
    )

    st.divider()
    st.subheader("Connexion")
    config = load_config()
    st.write(f"Base : `{config.get('database', 'shipdata')}`")
    st.write(f"Hôte : `{config.get('host', 'localhost')}`")

try:
    context = detect_ship_context()
    tables = get_tables()
except Exception as error:
    st.error("Connexion impossible à la base PostgreSQL.")
    st.write("Vérifie le fichier `config.json`, le nom de la base, l'utilisateur et le mot de passe.")
    st.exception(error)
    st.stop()

if context is None:
    st.warning("Je n'ai pas trouvé de table principale de navires.")
    st.write("L'interface cherche une table dont le nom contient `navire`, `vessel`, `ship` ou `bateau`.")
    st.write("Tables détectées :")
    st.dataframe(tables, use_container_width=True)
    st.stop()

if page == "Accueil":
    st.header("Présentation")
    st.write(
        "ShipData est une application de base de données qui permet de consulter et d'analyser "
        "des informations sur des navires internationaux."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tables détectées", len(tables))
    with col2:
        st.metric("Table principale", context["table"])
    with col3:
        try:
            st.metric("Navires", metric_count(context))
        except Exception:
            st.metric("Navires", "n/a")

    st.subheader("Ce que l'application permet de faire")
    st.markdown(
        """
- rechercher un navire par nom ou numéro IMO ;
- filtrer la flotte par type ou pavillon ;
- comparer les navires selon leur âge, leur tonnage ou leur catégorie ;
- afficher des graphiques simples ;
- exécuter les requêtes SQL prévues dans le projet ;
- tester une requête `SELECT` personnalisée.
        """
    )

    st.subheader("Colonnes détectées dans la table principale")
    detected = pd.DataFrame(
        [
            ["IMO", context.get("imo")],
            ["Nom", context.get("name")],
            ["Type", context.get("type")],
            ["Année de construction", context.get("year")],
            ["Pavillon", context.get("flag")],
            ["Tonnage", context.get("tonnage")],
            ["Société de classification", context.get("classification")],
            ["Constructeur", context.get("builder")],
            ["Propriétaire", context.get("owner")],
            ["Gestionnaire", context.get("manager")],
        ],
        columns=["Information", "Colonne détectée"],
    )
    st.dataframe(detected, use_container_width=True)

elif page == "Explorer les navires":
    st.header("Explorer les navires")

    col1, col2, col3 = st.columns(3)
    with col1:
        search_text = st.text_input("Recherche par nom ou IMO")
    with col2:
        selected_type = st.selectbox("Type de navire", get_distinct_values(context, context.get("type")))
    with col3:
        selected_flag = st.selectbox("Pavillon", get_distinct_values(context, context.get("flag")))

    sql, params = build_filter_query(context, search_text, selected_type, selected_flag)

    with st.expander("Voir la requête SQL utilisée"):
        st.code(sql, language="sql")

    try:
        df = run_query(sql, params)
        st.write(f"Résultats affichés : {len(df)}")
        st.dataframe(df, use_container_width=True)
    except Exception as error:
        st.error("La requête n'a pas pu être exécutée.")
        st.exception(error)

elif page == "Analyses":
    st.header("Analyses rapides")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre de navires", metric_count(context))
    with col2:
        avg_tonnage = metric_average(context, context.get("tonnage"))
        st.metric("Tonnage moyen", "n/a" if avg_tonnage is None else round(avg_tonnage, 2))
    with col3:
        avg_year = metric_average(context, context.get("year"))
        if avg_year is None:
            st.metric("Année moyenne", "n/a")
        else:
            st.metric("Année moyenne", round(avg_year, 1))

    chart_options = {
        "Types de navires": context.get("type"),
        "Pavillons": context.get("flag"),
        "Constructeurs": context.get("builder"),
        "Propriétaires": context.get("owner"),
        "Sociétés de classification": context.get("classification"),
    }
    available_options = {label: col for label, col in chart_options.items() if col is not None}

    if not available_options:
        st.warning("Aucune colonne catégorielle reconnue pour créer des graphiques.")
    else:
        selected_chart = st.selectbox("Analyse à afficher", list(available_options.keys()))
        df_chart = group_count(context, available_options[selected_chart], limit=15)
        st.dataframe(df_chart, use_container_width=True)
        if not df_chart.empty:
            st.bar_chart(df_chart.set_index("categorie"))

elif page == "Requêtes SQL":
    st.header("Requêtes SQL du projet")

    queries = predefined_queries(context)
    selected_query = st.selectbox("Choisir une requête prédéfinie", list(queries.keys()))
    sql = queries[selected_query]

    st.code(sql, language="sql")

    if st.button("Exécuter la requête"):
        try:
            df = run_query(sql)
            st.dataframe(df, use_container_width=True)
        except Exception as error:
            st.error("Erreur pendant l'exécution de la requête.")
            st.exception(error)

    st.divider()
    st.subheader("Requête personnalisée")
    st.write("Par sécurité, seules les requêtes qui commencent par `SELECT` sont acceptées ici.")
    custom_sql = st.text_area("Écrire une requête SELECT", height=180)

    if st.button("Exécuter ma requête"):
        if not safe_custom_query(custom_sql):
            st.error("Requête refusée. Utilise uniquement une requête SELECT.")
        else:
            try:
                df = run_query(custom_sql)
                st.dataframe(df, use_container_width=True)
            except Exception as error:
                st.error("La requête personnalisée n'a pas fonctionné.")
                st.exception(error)

elif page == "Structure de la base":
    st.header("Structure de la base")

    st.subheader("Tables")
    st.dataframe(tables, use_container_width=True)

    st.subheader("Colonnes")
    st.dataframe(get_columns(), use_container_width=True)

    st.subheader("Aperçu d'une table")
    table_labels = [f"{row['table_schema']}.{row['table_name']}" for _, row in tables.iterrows()]
    selected_table = st.selectbox("Choisir une table", table_labels)
    schema, table = selected_table.split(".", 1)
    preview_sql = f"SELECT * FROM {quote_ident(schema)}.{quote_ident(table)} LIMIT 100;"
    st.code(preview_sql, language="sql")
    st.dataframe(run_query(preview_sql), use_container_width=True)
