# Importation des bibliothèques nécessaires
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import matplotlib.pyplot as plt
import folium
from folium import plugins
from streamlit_folium import st_folium

# Ajouter cette configuration uniquement si exécuté directement
st.set_page_config(
    page_title="Analyse Bixi",
    page_icon="assets/bike-icon.svg",  # ou le chemin vers votre icône
    layout="wide")

# Définition des couleurs de la charte graphique BIXI
BIXI_COLORS = {
    'blue': '#2D2E83',    # Bleu BIXI pour les éléments d'interface
    'red': '#BC1E45',     # Rouge BIXI pour les données et visualisations
    'white': '#FFFFFF',   # Blanc pour les fonds
    'light_gray': '#F8F9FA'  # Gris clair pour les éléments secondaires
}

# CSS personnalisé pour le style de l'application
css = f"""
<style>
    /* Style général de l'application */
    .stApp {{
        background-color: {BIXI_COLORS['white']};
    }}
    
    /* Style de l'en-tête */
    .header-container {{
        padding: 2rem;
        background-color: {BIXI_COLORS['red']};
        color: {BIXI_COLORS['white']};
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        text-align: center;
    }}
    
    /* Style du titre principal */
    .main-title {{
        color: {BIXI_COLORS['white']};
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }}
    
    /* Style des cartes de métriques */
    .metric-card {{
        background-color: {BIXI_COLORS['white']};
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
        text-align: center;
    }}
    
    .metric-title {{
        color: {BIXI_COLORS['blue']};
        font-size: 1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        color: {BIXI_COLORS['red']};
        font-size: 1.5rem;
        font-weight: bold;
    }}
    
    /* Style des en-têtes de section */
    .section-header {{
        color: {BIXI_COLORS['blue']};
        font-size: 1.2rem;
        font-weight: bold;
        margin: 1.5rem 0;
        text-align: left;
    }}
    
    /* Design responsive */
    @media (max-width: 768px) {{
        .metric-card {{
            text-align: center;
            margin: 1rem 0;
        }}
        
        .section-header {{
            text-align: center;
        }}
    }}
    
    /* Style du sélecteur */
    div[data-baseweb="select"] {{
        background-color: {BIXI_COLORS['white']};
        border-radius: 8px;
        border: 2px solid {BIXI_COLORS['blue']};
    }}

    /* Style du conteneur de visualisation */
    .viz-container {{
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }}

    @media (max-width: 768px) {{
        .viz-container {{
            flex-direction: column;
        }}
    }}
</style>
"""

# Injection du CSS dans la page
st.markdown(css, unsafe_allow_html=True)

# Affichage de l'en-tête
st.markdown(f"""
    <div class="header-container">
        <h1 class="main-title">Analyse des données BIXI Montréal</h1>
    </div>
""", unsafe_allow_html=True)

# Fonction de chargement et analyse des données avec mise en cache
@st.cache_data
def charger_donnees(annee):
    """
    Charge et analyse les données BIXI pour une année spécifique.
    
    Args:
        annee (str): L'année pour laquelle charger les données
        
    Returns:
        dict: Dictionnaire contenant toutes les analyses calculées
    """
    resultats = {}
    chemin_bixis = './bixi_data'
    chemin_annee = os.path.join(chemin_bixis, str(annee))
    
    try:
        # Chargement du fichier des stations
        stations_file = f"Stations_{annee}.csv"
        stations_path = os.path.join(chemin_annee, stations_file)
        df_stations = pd.read_csv(stations_path)
        if len(df_stations.columns) == 1 and ';' in df_stations.columns[0]:
            df_stations = pd.read_csv(stations_path, sep=';')
            
        # Création du GeoDataFrame pour les stations
        geometry = [Point(xy) for xy in zip(df_stations['longitude'], df_stations['latitude'])]
        gdf_stations = gpd.GeoDataFrame(df_stations, geometry=geometry, crs="EPSG:4326")
        
        # Chargement des fichiers de trajets
        fichiers = [f for f in os.listdir(chemin_annee) 
                   if f.endswith('.csv') and not f.startswith('Stations')]
        
        df_list = []
        for fichier in fichiers:
            chemin_complet = os.path.join(chemin_annee, fichier)
            df = pd.read_csv(chemin_complet, low_memory=False)
            df_list.append(df)

        # Combinaison de tous les fichiers de trajets
        df_annee = pd.concat(df_list, ignore_index=True)
        df_annee['start_date'] = pd.to_datetime(df_annee['start_date'])
        df_annee['end_date'] = pd.to_datetime(df_annee['end_date'])

        # Calcul des différentes statistiques
        resultats['stations'] = gdf_stations
        resultats['duree_moyenne'] = df_annee['duration_sec'].mean() / 60
        
        trajets_boucle = df_annee[df_annee['start_station_code'] == df_annee['end_station_code']]
        resultats['proportion_boucle'] = (len(trajets_boucle) / len(df_annee)) * 100
        
        resultats['membres'] = len(df_annee[df_annee['is_member'] == 1])
        resultats['occasionnels'] = len(df_annee[df_annee['is_member'] == 0])
        
        # Analyse de la répartition par période
        df_annee['hour'] = df_annee['start_date'].dt.hour
        bins = [0, 6, 12, 18, 24]
        labels = ['0h-6h', '6h-12h', '12h-18h', '18h-24h']
        df_annee['period'] = pd.cut(df_annee['hour'], bins=bins, labels=labels, include_lowest=True)
        compte_periodes = df_annee['period'].value_counts()
        resultats['repartition_periodes'] = (compte_periodes / len(df_annee)) * 100

        return resultats
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None

def creer_carte(gdf_stations):
    """
    Crée une carte Folium avec les stations BIXI regroupées en clusters
    et un outil de mesure de distance.
    
    Args:
        gdf_stations (GeoDataFrame): DataFrame contenant les informations des stations
        
    Returns:
        folium.Map: Carte avec les stations en clusters
    """
    # Création de la carte de base avec CartoDB Positron comme fond par défaut
    carte = folium.Map(
        location=[45.5236, -73.5985],  # Centre de Montréal
        zoom_start=12,
        tiles='cartodbpositron',
        attr='© CartoDB © OpenStreetMap contributors'
    )
    
    # Ajout des différents fonds de carte avec leurs attributions
    folium.TileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        name='CartoDB Dark',
        attr='© CartoDB © OpenStreetMap contributors',
        control=True
    ).add_to(carte)
    
    folium.TileLayer(
        'https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}.jpg',
        name='Stamen Terrain',
        attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.',
        control=True
    ).add_to(carte)
    
    folium.TileLayer(
        'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        name='Google Satellite',
        attr='Google',
        control=True
    ).add_to(carte)
    
    folium.TileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        name='OpenStreetMap',
        attr='© OpenStreetMap contributors',
        control=True
    ).add_to(carte)
    
    # Ajout de l'outil de mesure
    plugins.MeasureControl(
        position='topleft',
        primary_length_unit='meters',
        secondary_length_unit='kilometers',
        primary_area_unit='sqmeters',
        secondary_area_unit='hectares',
        concatenate_words=True,
        active_color='#BC1E45',  # Couleur BIXI rouge
        completed_color='#2D2E83'  # Couleur BIXI bleue
    ).add_to(carte)
    
    # Création du groupe de marqueurs en cluster
    marker_cluster = plugins.MarkerCluster(
        name='Stations BIXI',
        overlay=True,
        control=True,
        icon_create_function="""
        function(cluster) {
            return L.divIcon({
                html: '<div style="background-color: #BC1E45; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-weight: bold;">' + cluster.getChildCount() + '</div>',
                className: 'marker-cluster-custom',
                iconSize: L.point(30, 30)
            });
        }
        """
    )
    
    # Ajout des marqueurs pour chaque station dans le cluster
    for _, station in gdf_stations.iterrows():
        folium.CircleMarker(
            location=[float(station.geometry.y), float(station.geometry.x)],
            radius=8,
            popup=f"""
                <div style='font-family: Arial; font-size: 12px;'>
                    <b>{station['name']}</b>
                </div>
            """,
            color=BIXI_COLORS['red'],
            fill=True,
            fill_color=BIXI_COLORS['red'],
            fill_opacity=0.7,
            weight=2
        ).add_to(marker_cluster)
    
    # Ajout du groupe de clusters à la carte
    marker_cluster.add_to(carte)
    
    # Ajout d'une mini-carte
    minimap = plugins.MiniMap(toggle_display=True)
    carte.add_child(minimap)
    
    # Ajout d'un bouton plein écran
    plugins.Fullscreen(
        position='topleft',
        title='Plein écran',
        title_cancel='Quitter le plein écran',
        force_separate_button=True
    ).add_to(carte)
    
    # Ajout du contrôle de couches
    folium.LayerControl(position='topright').add_to(carte)
    
    return carte

def main():
    # Liste des années disponibles
    chemin_bixis = './bixi_data'
    annees_disponibles = [d for d in os.listdir(chemin_bixis) 
                        if os.path.isdir(os.path.join(chemin_bixis, d))]
    annees_disponibles.sort()

    # Création du sélecteur d'année
    with st.container():
        annee_selectionnee = st.selectbox(
            'Sélectionnez une année',
            annees_disponibles,
            index=annees_disponibles.index('2014')  # 2014 par défaut
        )

    # Chargement et affichage des données
    resultats_annee = charger_donnees(annee_selectionnee)

    if resultats_annee:
        # Affichage des métriques principales
        st.markdown('<div class="section-header">Statistiques générales</div>', unsafe_allow_html=True)
        
        # Création des colonnes pour les métriques
        col1, col2, col3, col4 = st.columns(4)
        
        # Affichage de chaque métrique dans sa carte
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Durée moyenne des trajets</div>
                    <div class="metric-value">{resultats_annee['duree_moyenne']:.1f} min</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Proportion de boucles</div>
                    <div class="metric-value">{resultats_annee['proportion_boucle']:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Trajets membres</div>
                    <div class="metric-value">{resultats_annee['membres']:,}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Trajets occasionnels</div>
                    <div class="metric-value">{resultats_annee['occasionnels']:,}</div>
                </div>
            """, unsafe_allow_html=True)

        # Espacement
        st.markdown('<br>', unsafe_allow_html=True)
        
        # Création des colonnes pour les visualisations
        col_carte, col_graphe = st.columns(2, gap="small")
        
        # Affichage de la carte
        with col_carte:
            st.markdown(f"""<div class="section-header">Stations BIXI {annee_selectionnee} </div>""", unsafe_allow_html=True)
            carte = creer_carte(resultats_annee['stations'])
            st_folium(carte, width=None, height=500)
        
        # Création et affichage du graphique
        with col_graphe:
            st.markdown('<div class="section-header">Répartition des trajets par période</div>', unsafe_allow_html=True)
            
            # Configuration du style matplotlib
            plt.style.use('seaborn-v0_8-whitegrid')
            
            # Création de la figure
            fig, ax = plt.subplots(figsize=(10, 8))
            donnees_triees = resultats_annee['repartition_periodes'].sort_values(ascending=False)
            
            # Création du graphique à barres
            bars = donnees_triees.plot(
                kind='bar',
                ax=ax,
                color=BIXI_COLORS['red'],
                width=0.7
            )
            
            # Personnalisation des axes et du style
            plt.xticks(rotation=45)
            ax.set_ylabel('')  # Suppression du ylabel
            ax.tick_params(colors=BIXI_COLORS['blue'])
            
            # Suppression des bordures du graphique
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Configuration de la grille
            ax.yaxis.grid(True, linestyle='--', alpha=0.7)
            ax.set_axisbelow(True)
            
            # Ajustement des marges
            plt.tight_layout(pad=0.5)
            
            # Affichage du graphique
            st.pyplot(fig)

        # Ajout du footer
        st.markdown(f"""
            <div style='text-align: center; color: #666; padding: 20px; margin-top: 0.5rem;'>
                Données BIXI Montréal - Par Laouali ADA AYA LinKedin: <a href="https://www.linkedin.com/in/laouali-ada-aya-7139ab195/" target="_blank">Laouali ADA AYA</a>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
