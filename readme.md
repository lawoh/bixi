# Application d'Analyse BIXI Montréal

## Description
Cette application Streamlit permet de visualiser et d'analyser les données du service de vélos en libre-service BIXI à Montréal. Elle offre une interface interactive pour explorer les statistiques d'utilisation, la localisation des stations et les tendances d'utilisation.

## Fonctionnalités

- 📊 Visualisation des statistiques clés :
  - Durée moyenne des trajets
  - Proportion de boucles (trajets retour à la station de départ)
  - Nombre de trajets par type d'utilisateur (membres vs occasionnels)

- 🗺️ Carte interactive des stations :
  - Visualisation de toutes les stations BIXI
  - Regroupement en clusters pour une meilleure lisibilité
  - Différents fonds de carte disponibles
  - Outil de mesure de distances

- 📈 Analyse temporelle :
  - Répartition des trajets par période de la journée
  - Visualisation graphique des tendances

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/lawoh/bixi.git
cd bixi
```

2. Créez et activez un environnement virtuel (recommandé) :
```bash
python -m venv bixi_env
source bixi_env/bin/activate  # Sur Unix/macOS
# ou
bixi_env\Scripts\activate  # Sur Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Structure des données

L'application s'attend à trouver les données BIXI dans un dossier `bixi_data` avec la structure suivante :
```
bixi_data/
├── 2014/
│   ├── Stations_2014.csv
│   └── [fichiers de trajets].csv
├── 2015/
│   ├── Stations_2015.csv
│   └── [fichiers de trajets].csv
└── ...
```

## Utilisation

1. Placez vos données BIXI dans le dossier `bixi_data`
2. Lancez l'application :
```bash
streamlit run app.py
```
3. Ouvrez votre navigateur à l'adresse : `http://localhost:8501`

## Déploiement

Cette application peut être déployée sur Streamlit Cloud :
1. Créez un compte sur [share.streamlit.io](https://share.streamlit.io)
2. Connectez votre dépôt GitHub
3. Déployez l'application

## Technologies utilisées

- [Streamlit](https://streamlit.io/) - Framework web
- [Folium](https://python-folium.readthedocs.io/) - Cartographie interactive
- [Pandas](https://pandas.pydata.org/) - Analyse de données
- [GeoPandas](https://geopandas.org/) - Données géospatiales
- [Matplotlib](https://matplotlib.org/) - Visualisation de données


## Licence

Distribué sous la licence MIT. Voir `LICENSE` pour plus d'informations.

## Contact

Lien du projet : [https://github.com/lawoh/bixi.git]
