# app_pollution.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import scatter_matrix


st.set_page_config(page_title="Analyse de la qualité de l'air", layout="wide")


#  CHARGEMENT DES DONNÉES
st.title(" Étude de la Qualité de l’air et Pollution")
fichier = "pollution.csv"

@st.cache_data
def charger_donnees(fichier):
    data = pd.read_csv(fichier)
    return data

data = charger_donnees(fichier)


menu = st.sidebar.radio(
    " Navigation",
    [
        "Aperçu général",
        "Valeurs manquantes",
        "Analyse descriptive",
        "Visualisations",
        "Corrélations"
    ]
)

if menu == "Aperçu général":
    st.header(" Aperçu des données brutes")
    st.dataframe(data.head(10))

    st.subheader("Types de variables")
    st.write(data.dtypes)

    st.subheader("Dimensions du jeu de données")
    st.write(f"**{data.shape[0]}** lignes et **{data.shape[1]}** colonnes")
#  VALEURS MANQUANTES

elif menu == "Valeurs manquantes":
    st.header(" Analyse des valeurs manquantes")

    dataMissing = pd.DataFrame({
        'Valeurs_manquantes': data.isnull().sum(),
        'Pourcentage_manquant (%)': data.isnull().mean() * 100
    }).sort_values(by='Valeurs_manquantes', ascending=False)

    st.dataframe(dataMissing.style.background_gradient(cmap='Reds'))

    st.download_button(
        " Télécharger le rapport CSV",
        dataMissing.to_csv().encode('utf-8'),
        "rapport_valeurs_manquantes.csv",
        "text/csv"
    )

    st.subheader(" Heatmap des valeurs manquantes")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(data.isnull(), cmap='plasma', cbar=False, ax=ax)
    st.pyplot(fig)

# ANALYSE DESCRIPTIVE
elif menu == "Analyse descriptive":
    st.header(" Statistiques descriptives")

    st.subheader("Description statistique")
    st.dataframe(data.describe())

    st.subheader("Répartition des classes de qualité d'air")
    if 'Qualite_air' in data.columns:
        count_classe = data['Qualite_air'].value_counts().reset_index()
        count_classe.columns = ['Classe', 'Nombre']
        count_classe['Pourcentage'] = (count_classe['Nombre'] / len(data) * 100).round(2)
        st.dataframe(count_classe)

        fig, ax = plt.subplots()
        sns.barplot(data=count_classe, x='Classe', y='Nombre', palette='viridis', ax=ax)
        st.pyplot(fig)
    else:
        st.warning(" La colonne 'Qualite_air' n'existe pas dans ce fichier.")

# VISUALISATIONS
elif menu == "Visualisations":
    st.header(" Visualisations des variables")

    option = st.selectbox("Choisir le type de graphique :", ["Histogrammes", "Densité", "Boîtes à moustaches", "Scatter Matrix", "Pairplot"])

    if option == "Histogrammes":
        st.subheader("📦 Histogrammes")
        fig, ax = plt.subplots(figsize=(12, 8))
        data.hist(bins=20, figsize=(12, 8), grid=True)
        st.pyplot(fig)

    elif option == "Densité":
        st.subheader(" Graphiques de densité")
        fig = data.plot(kind='density', subplots=True, layout=(4, 3), sharex=False, figsize=(12, 10))
        st.pyplot(plt.gcf())

    elif option == "Boîtes à moustaches":
        st.subheader(" Boxplots")
        fig = data.plot(kind='box', subplots=True, layout=(4, 3), sharex=False, figsize=(12, 10))
        st.pyplot(plt.gcf())

    elif option == "Scatter Matrix":
        st.subheader(" Matrice de dispersion")
        fig = scatter_matrix(data, figsize=(10, 10), diagonal='kde', color='green')
        st.pyplot(plt.gcf())

    elif option == "Pairplot":
        if 'Qualite_air' in data.columns:
            st.subheader(" Pairplot coloré par qualité de l’air")
            fig = sns.pairplot(data, hue='Qualite_air')
            st.pyplot(fig)
        else:
            st.warning("⚠️ Impossible d’afficher le pairplot : colonne 'Qualite_air' absente.")

#  CORRÉLATIONS
elif menu == "Corrélations":
    st.header(" Analyse de corrélation")

    # Nettoyage et conversion
    for col in data.columns:
        if data[col].dtype == 'object':
            data[col] = data[col].replace(r'[^0-9.\-]', '', regex=True)
            data[col] = pd.to_numeric(data[col], errors='coerce')

    if 'Qualite_air' in data.columns:
        mapping = {'bon': 0, 'moyen': 1, 'mauvais': 2, 'dangereuse': 3}
        data['class_num'] = data['Qualite_air'].map(mapping)

        corr = data.corr(numeric_only=True, method='pearson')
        st.subheader(" Matrice de corrélation (Pearson)")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="pink", ax=ax)
        st.pyplot(fig)

        # Corrélation spécifique avec la qualité de l'air
        if 'class_num' in corr.columns:
            corr_qualite = corr['class_num'].drop('class_num', errors='ignore').sort_values(ascending=False)
            st.subheader("🌿 Corrélation avec la qualité de l'air")
            st.bar_chart(corr_qualite)
    else:
        st.warning(" La colonne 'Qualite_air' n’existe pas dans ce fichier.")
