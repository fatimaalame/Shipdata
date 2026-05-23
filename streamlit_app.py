# streamlit_app.py
# Interface simple pour le projet ShipDATA

import streamlit as st
import pandas as pd
from pathlib import Path


# Configuration de la page
st.set_page_config(
    page_title="ShipDATA",
    page_icon="🚢",
    layout="wide"
)


# Dossier où on mettra les fichiers CSV
DATA_DIR = Path("Data")


# Fonction pour charger un CSV
# @st.cache_data évite de recharger le fichier à chaque clic
@st.cache_data
def load_csv(file_name):
    file_path = DATA_DIR / file_name

    if not file_path.exists():
        return None

    return pd.read_csv(file_path)


# Titre principal
st.title("🚢 ShipDATA")
st.write("Interface simple pour explorer les données maritimes du projet de base de données.")


# Menu latéral
page = st.sidebar.radio(
    "Navigation",
    [
        "Accueil",
        "Navires",
        "Ports",
        "Escales",
        "Requêtes SQL",
        "À propos"
    ]
)


# Page d'accueil
if page == "Accueil":
    st.header("Bienvenue")

    st.write(
        """
        Cette application permet de visualiser les données du projet ShipDATA.

        L’objectif du projet est de construire une base de données relationnelle
        autour des navires, ports, pavillons, propriétaires, constructeurs,
        sociétés de classification et escales.
        """
    )

    st.info("Commence par ajouter tes fichiers CSV dans le dossier Data.")


# Page Navires
elif page == "Navires":
    st.header("Navires")

    df_navires = load_csv("NAVIRE.csv")

    if df_navires is None:
        st.warning("Le fichier Data/NAVIRE.csv n'existe pas encore.")
    else:
        st.write("Aperçu des données des navires :")
        st.dataframe(df_navires)

        st.subheader("Statistiques rapides")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Nombre de navires", len(df_navires))

        with col2:
            if "nom_navire" in df_navires.columns:
                st.metric("Noms de navires renseignés", df_navires["nom_navire"].notna().sum())


# Page Ports
elif page == "Ports":
    st.header("Ports")

    df_ports = load_csv("PORT_DATA.csv")

    if df_ports is None:
        st.warning("Le fichier Data/PORT_DATA.csv n'existe pas encore.")
    else:
        st.write("Aperçu des données des ports :")
        st.dataframe(df_ports)

        st.subheader("Statistiques rapides")
        st.metric("Nombre de ports", len(df_ports))


# Page Escales
elif page == "Escales":
    st.header("Escales")

    df_escales = load_csv("ESCALES.csv")

    if df_escales is None:
        st.warning("Le fichier Data/ESCALES.csv n'existe pas encore.")
    else:
        st.write("Aperçu des données des escales :")
        st.dataframe(df_escales)

        st.subheader("Statistiques rapides")
        st.metric("Nombre d'escales", len(df_escales))


# Page Requêtes SQL
elif page == "Requêtes SQL":
    st.header("Requêtes SQL")

    st.write(
        """
        Cette section servira à présenter les requêtes principales du projet :
        jointures, agrégations, filtres, analyses par pavillon, port, type de navire, etc.
        """
    )

    st.code(
        """
SELECT n.nom_navire, t.nom_type, p.nom_pays
FROM navire n
JOIN types_navires t ON n.id_type_navire = t.id_type_navire
JOIN pavillons p ON n.id_pavillon = p.id_pavillon;
        """,
        language="sql"
    )


# Page À propos
elif page == "À propos":
    st.header("À propos du projet")

    st.write(
        """
        ShipDATA est un projet universitaire de base de données relationnelle.

        Le but est de modéliser, créer, remplir et interroger une base de données
        liée au domaine maritime.
        """
    )