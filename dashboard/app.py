"""
Dashboard Streamlit - Retail Geodata Analytics
Tableau de bord interactif pour l'analyse retail géospatiale
"""

import streamlit as st

# Configuration de la page - DOIT ÊTRE EN PREMIER
st.set_page_config(
    page_title="Retail Geodata Analytics",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static
import sys
import os

# Ajout du chemin pour importer nos modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
scripts_path = os.path.join(project_root, 'scripts')
sys.path.append(scripts_path)

# Variables pour les modules
CAPredictor = None
CompetitiveImpactAnalyzer = None

# Tentative d'import des modules - versions robustes d'abord
try:
    from ca_predictor_simple import CAPredictor, create_demo_predictor
    PREDICTOR_AVAILABLE = True
except ImportError:
    try:
        from ca_predictor_clean import CAPredictor
        PREDICTOR_AVAILABLE = True
    except ImportError:
        PREDICTOR_AVAILABLE = False
    
try:
    from competitive_analysis_clean import CompetitiveImpactAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    try:
        from competitive_analysis_simple import CompetitiveImpactAnalyzer
        ANALYZER_AVAILABLE = True
    except ImportError:
        ANALYZER_AVAILABLE = False

# Message de statut discret seulement en cas de problème
if not PREDICTOR_AVAILABLE or not ANALYZER_AVAILABLE:
    st.info("ℹ️ Certaines fonctionnalités ML avancées ne sont pas disponibles. Le dashboard fonctionne en mode standard.")

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charge les données avec cache"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_path = os.path.join(project_root, 'data')
        
        magasins = pd.read_csv(os.path.join(data_path, 'magasins_performance.csv'))
        concurrents = pd.read_csv(os.path.join(data_path, 'sites_concurrents.csv'))
        return magasins, concurrents
    except FileNotFoundError as e:
        st.error(f"❌ Fichiers de données non trouvés: {e}")
        st.info("💡 Exécutez d'abord le script generate_data.py depuis le dossier scripts/")
        return None, None

def create_performance_map(df):
    """Crée une carte de performance des magasins"""
    
    # Normalisation du CA pour la taille des marqueurs
    df['ca_normalized'] = (df['ca_annuel'] - df['ca_annuel'].min()) / (df['ca_annuel'].max() - df['ca_annuel'].min())
    df['marker_size'] = 5 + df['ca_normalized'] * 15
    
    # Couleurs par enseigne
    color_map = {'SuperFrais': '#1f77b4', 'MarchéPlus': '#ff7f0e', 'BioNature': '#2ca02c', 
                'CityMarket': '#d62728', 'FamilyShop': '#9467bd'}
    df['color'] = df['enseigne'].map(color_map)
    
    # Création de la carte
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    fig = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        size='marker_size',
        color='enseigne',
        hover_name='id_magasin',
        hover_data={
            'ville': True,
            'ca_annuel': ':,.0f',
            'panier_moyen': ':.2f',
            'nb_clients_mois': ':,',
            'marker_size': False
        },
        mapbox_style="open-street-map",
        zoom=5,
        height=600,
        title="Répartition géographique et performance des magasins"
    )
    
    fig.update_layout(mapbox=dict(center=dict(lat=center_lat, lon=center_lon)))
    
    return fig

def create_performance_charts(df):
    """Crée les graphiques de performance"""
    
    # Métriques par enseigne
    perf_enseigne = df.groupby('enseigne').agg({
        'ca_annuel': ['mean', 'sum', 'count'],
        'panier_moyen': 'mean',
        'nb_clients_mois': 'mean'
    }).round(0)
    
    perf_enseigne.columns = ['CA_moyen', 'CA_total', 'Nb_magasins', 'Panier_moyen', 'Clients_mois']
    perf_enseigne = perf_enseigne.reset_index()
    
    # Graphiques
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('CA moyen par enseigne', 'Panier moyen par enseigne', 
                       'Distribution du CA', 'CA vs Population'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "histogram"}, {"type": "scatter"}]]
    )
    
    # CA moyen par enseigne
    fig.add_trace(
        go.Bar(x=perf_enseigne['enseigne'], y=perf_enseigne['CA_moyen'], 
               name='CA moyen', marker_color='skyblue'),
        row=1, col=1
    )
    
    # Panier moyen par enseigne
    fig.add_trace(
        go.Bar(x=perf_enseigne['enseigne'], y=perf_enseigne['Panier_moyen'], 
               name='Panier moyen', marker_color='lightgreen'),
        row=1, col=2
    )
    
    # Distribution du CA
    fig.add_trace(
        go.Histogram(x=df['ca_annuel']/1000, name='Distribution CA', 
                    marker_color='coral', nbinsx=15),
        row=2, col=1
    )
    
    # CA vs Population
    fig.add_trace(
        go.Scatter(x=df['population_zone_1km'], y=df['ca_annuel']/1000,
                  mode='markers', name='CA vs Population',
                  marker=dict(color='gold', size=8)),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Analyses de performance")
    fig.update_xaxes(title_text="Enseigne", row=1, col=1)
    fig.update_xaxes(title_text="Enseigne", row=1, col=2)
    fig.update_xaxes(title_text="CA (k€)", row=2, col=1)
    fig.update_xaxes(title_text="Population zone 1km", row=2, col=2)
    fig.update_yaxes(title_text="CA moyen (€)", row=1, col=1)
    fig.update_yaxes(title_text="Panier moyen (€)", row=1, col=2)
    fig.update_yaxes(title_text="Fréquence", row=2, col=1)
    fig.update_yaxes(title_text="CA (k€)", row=2, col=2)
    
    return fig

def prediction_interface(magasins_df):
    """Interface de prédiction de CA"""
    
    st.subheader("🎯 Simulateur de CA pour nouvelle implantation")
    
    # Formulaire de saisie
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            enseigne = st.selectbox("Enseigne", magasins_df['enseigne'].unique())
            format_mag = st.selectbox("Format", magasins_df['format'].unique())
            # Nettoyer les villes pour le selectbox
            villes_clean = magasins_df['ville'].dropna().astype(str)
            villes_unique = [v for v in villes_clean.unique() if v.strip() and v != 'nan']
            ville = st.selectbox("Ville", sorted(villes_unique))
            surface = st.number_input("Surface de vente (m²)", min_value=100, max_value=5000, value=1000)
            effectif = st.number_input("Effectif", min_value=5, max_value=100, value=20)
            population = st.number_input("Population zone 1km", min_value=1000, max_value=50000, value=15000)
        
        with col2:
            densite = st.number_input("Densité hab/km²", min_value=100, max_value=10000, value=3000)
            revenu = st.number_input("Revenu médian zone (€)", min_value=15000, max_value=60000, value=30000)
            age_moyen = st.number_input("Age moyen zone", min_value=20.0, max_value=60.0, value=40.0)
            concurrents_500m = st.number_input("Concurrents 500m", min_value=0, max_value=10, value=1)
            parking = st.number_input("Places de parking", min_value=20, max_value=500, value=100)
            transport = st.slider("Score transport (1-10)", min_value=1, max_value=10, value=7)
        
        zone_commerciale = st.checkbox("Zone commerciale")
        
        submitted = st.form_submit_button("🚀 Prédire le CA")
        
        if submitted:
            # Préparation des données pour la prédiction
            nouveau_site = {
                'enseigne': enseigne,
                'format': format_mag,
                'ville': ville,
                'surface_vente': surface,
                'effectif': effectif,
                'population_zone_1km': population,
                'densite_hab_km2': densite,
                'revenu_median_zone': revenu,
                'age_moyen_zone': age_moyen,
                'concurrents_500m': concurrents_500m,
                'concurrents_1km': concurrents_500m + 2,  # Estimation
                'parking_places': parking,
                'distance_centre_ville': 3.0,  # Valeur par défaut
                'transport_score': transport,
                'zone_commerciale': zone_commerciale,
                'date_ouverture': '2024-01-01'
            }
            
            try:
                # Simulation de prédiction (remplacer par le vrai modèle)
                # En attendant, on fait une estimation basique
                ca_base = (population * 25 + revenu * 10 + surface * 400 + 
                          parking * 1000 + transport * 30000 - concurrents_500m * 100000)
                ca_predit = max(300000, ca_base * np.random.normal(1, 0.1))
                
                # Affichage du résultat
                st.success(f"💰 **CA prédit: {ca_predit:,.0f}€**")
                
                # Comparaison avec la moyenne
                ca_moyen_enseigne = magasins_df[magasins_df['enseigne'] == enseigne]['ca_annuel'].mean()
                ecart = (ca_predit - ca_moyen_enseigne) / ca_moyen_enseigne * 100
                
                if ecart > 0:
                    st.info(f"📈 {ecart:.1f}% au-dessus de la moyenne {enseigne}")
                else:
                    st.warning(f"📉 {abs(ecart):.1f}% en-dessous de la moyenne {enseigne}")
                
                # Recommandations
                st.subheader("💡 Recommandations")
                if population < 10000:
                    st.warning("⚠️ Population zone faible - Considérer un format plus petit")
                if concurrents_500m > 3:
                    st.warning("⚠️ Zone très concurrentielle - Risque d'impact négatif")
                if transport < 5:
                    st.warning("⚠️ Accessibilité limitée - Prévoir plus de parking")
                
            except Exception as e:
                st.error(f"❌ Erreur de prédiction: {str(e)}")

def main():
    """Application principale"""
    
    # En-tête
    st.markdown('<h1 class="main-header">🏪 Retail Geodata Analytics</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Chargement des données
    magasins_df, concurrents_df = load_data()
    
    if magasins_df is None:
        st.stop()
    
    # Nettoyage et validation des données
    try:
        # S'assurer que la colonne ville est bien formatée
        if 'ville' in magasins_df.columns:
            magasins_df['ville'] = magasins_df['ville'].astype(str)
            # Supprimer les lignes avec des villes invalides
            magasins_df = magasins_df[
                (magasins_df['ville'].notna()) & 
                (magasins_df['ville'] != 'nan') & 
                (magasins_df['ville'].str.strip() != '')
            ]
    except Exception as e:
        st.error(f"Erreur dans le nettoyage des données: {e}")
        st.stop()
    
    # Sidebar pour la navigation
    st.sidebar.markdown('<div class="sidebar-header">🧭 Navigation</div>', unsafe_allow_html=True)
    
    pages = {
        "🏠 Vue d'ensemble": "overview",
        "📊 Analyses de performance": "performance", 
        "🗺️ Cartographie": "mapping",
        "🎯 Prédiction CA": "prediction",
        "⚔️ Impact concurrentiel": "competition"
    }
    
    selected_page = st.sidebar.selectbox("Choisir une page", list(pages.keys()))
    page_key = pages[selected_page]
    
    # Filtres dans la sidebar
    st.sidebar.markdown('<div class="sidebar-header">🔍 Filtres</div>', unsafe_allow_html=True)
    
    # Filtre par enseigne
    enseignes_selected = st.sidebar.multiselect(
        "Enseignes", 
        magasins_df['enseigne'].unique(),
        default=magasins_df['enseigne'].unique()
    )
    
    # Filtre par ville
    # Nettoyer les valeurs de ville (supprimer NaN et valeurs vides)
    villes_clean = magasins_df['ville'].dropna().astype(str)
    villes_unique = [v for v in villes_clean.unique() if v.strip() and v != 'nan']
    villes_sorted = sorted(villes_unique)
    
    villes_selected = st.sidebar.multiselect(
        "Villes",
        villes_sorted,
        default=villes_sorted
    )
    
    # Filtrage des données
    df_filtered = magasins_df[
        (magasins_df['enseigne'].isin(enseignes_selected)) &
        (magasins_df['ville'].isin(villes_selected))
    ]
    
    # Affichage selon la page sélectionnée
    if page_key == "overview":
        # Vue d'ensemble
        st.header("📈 Vue d'ensemble du réseau")
        
        # KPIs principaux
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏪 Magasins", len(df_filtered))
        
        with col2:
            ca_total = df_filtered['ca_annuel'].sum()
            st.metric("💰 CA Total", f"{ca_total:,.0f}€")
        
        with col3:
            ca_moyen = df_filtered['ca_annuel'].mean()
            st.metric("📊 CA Moyen", f"{ca_moyen:,.0f}€")
        
        with col4:
            panier_moyen = df_filtered['panier_moyen'].mean()
            st.metric("🛒 Panier Moyen", f"{panier_moyen:.2f}€")
        
        # Graphique de répartition
        col1, col2 = st.columns(2)
        
        with col1:
            # CA par enseigne
            ca_par_enseigne = df_filtered.groupby('enseigne')['ca_annuel'].sum()
            fig_pie = px.pie(values=ca_par_enseigne.values, names=ca_par_enseigne.index,
                           title="Répartition du CA par enseigne")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Magasins par ville
            mag_par_ville = df_filtered['ville'].value_counts().head(10)
            fig_bar = px.bar(x=mag_par_ville.index, y=mag_par_ville.values,
                           title="Top 10 - Magasins par ville")
            fig_bar.update_xaxes(title="Ville")
            fig_bar.update_yaxes(title="Nombre de magasins")
            st.plotly_chart(fig_bar, use_container_width=True)
    
    elif page_key == "performance":
        # Analyses de performance
        st.header("📊 Analyses de performance")
        
        # Graphiques de performance
        fig_perf = create_performance_charts(df_filtered)
        st.plotly_chart(fig_perf, use_container_width=True)
        
        # Tableau de performance détaillé
        st.subheader("📋 Performance détaillée")
        
        # Colonnes à afficher
        columns_display = ['id_magasin', 'enseigne', 'ville', 'ca_annuel', 
                          'panier_moyen', 'nb_clients_mois', 'surface_vente']
        
        df_display = df_filtered[columns_display].sort_values('ca_annuel', ascending=False)
        st.dataframe(df_display, use_container_width=True)
    
    elif page_key == "mapping":
        # Cartographie
        st.header("🗺️ Cartographie des magasins")
        
        # Carte de performance
        fig_map = create_performance_map(df_filtered)
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Statistiques géographiques
        st.subheader("📍 Statistiques par ville")
        
        stats_ville = df_filtered.groupby('ville').agg({
            'ca_annuel': ['sum', 'mean', 'count'],
            'panier_moyen': 'mean'
        }).round(0)
        
        stats_ville.columns = ['CA_total', 'CA_moyen', 'Nb_magasins', 'Panier_moyen']
        stats_ville = stats_ville.reset_index().sort_values('CA_total', ascending=False)
        
        st.dataframe(stats_ville, use_container_width=True)
    
    elif page_key == "prediction":
        # Prédiction de CA
        prediction_interface(magasins_df)
    
    elif page_key == "competition":
        # Analyse concurrentielle
        st.header("⚔️ Analyse d'impact concurrentiel")
        
        if concurrents_df is not None:
            st.subheader("🎯 Concurrents identifiés")
            
            # Affichage des concurrents
            st.dataframe(concurrents_df[['id_site', 'type_concurrent', 'surface_prevue', 
                                       'zone_chalandise_km', 'ouverture_prevue']], 
                        use_container_width=True)
            
            # Sélection d'un concurrent pour analyse
            concurrent_selected = st.selectbox("Analyser l'impact du concurrent:", 
                                             concurrents_df['id_site'].tolist())
            
            if st.button("🔍 Analyser l'impact"):
                try:
                    # Initialisation de l'analyseur
                    analyzer = CompetitiveImpactAnalyzer(magasins_df, concurrents_df)
                    
                    # Vérification que la méthode existe
                    if not hasattr(analyzer, 'analyze_scenario'):
                        st.error("❌ Méthode analyze_scenario non disponible. Utilisation du module de fallback.")
                        st.stop()
                    
                    # Analyse de l'impact
                    with st.spinner(f"Analyse en cours pour {concurrent_selected}..."):
                        impacts = analyzer.analyze_scenario(concurrent_selected)
                    
                    if impacts is not None:
                        # Affichage des résultats
                        magasins_impactes = impacts[impacts['dans_zone'] == True]
                        
                        if len(magasins_impactes) > 0:
                            st.success(f"✅ Analyse terminée pour {concurrent_selected}")
                            
                            # Métriques de résumé
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("🏪 Magasins impactés", len(magasins_impactes))
                            with col2:
                                perte_totale = magasins_impactes['perte_ca_estimee'].sum()
                                st.metric("� Perte totale", f"{perte_totale:,.0f}€")
                            with col3:
                                impact_moyen = magasins_impactes['impact_percent'].mean()
                                st.metric("📉 Impact moyen", f"{impact_moyen:.1%}")
                            
                            # Détail par magasin
                            st.subheader("📊 Détail par magasin impacté")
                            detail_display = magasins_impactes[[
                                'id_magasin', 'magasin_ville', 'distance_km', 
                                'impact_percent', 'perte_ca_estimee'
                            ]].sort_values('perte_ca_estimee', ascending=False)
                            
                            detail_display['impact_percent'] = detail_display['impact_percent'].apply(lambda x: f"{x:.1%}")
                            detail_display['perte_ca_estimee'] = detail_display['perte_ca_estimee'].apply(lambda x: f"{x:,.0f}€")
                            detail_display['distance_km'] = detail_display['distance_km'].apply(lambda x: f"{x:.1f}km")
                            
                            st.dataframe(detail_display, use_container_width=True)
                            
                        else:
                            st.info(f"✅ Aucun magasin impacté par {concurrent_selected}")
                            st.write("Ce concurrent est situé en dehors des zones de chalandise de nos magasins.")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
                    st.write("Vérifiez que tous les modules sont correctement installés.")
        else:
            st.warning("❌ Données de concurrents non disponibles")

if __name__ == "__main__":
    main()