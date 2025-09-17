"""
Script de diagnostic pour l'analyse concurrentielle
Vérification des distances et paramètres d'impact
"""

import pandas as pd
import numpy as np
from geopy.distance import geodesic
import sys
import os

# Ajout du chemin pour importer nos modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
scripts_path = os.path.join(project_root, 'scripts')
sys.path.append(scripts_path)

from competitive_analysis_clean import CompetitiveImpactAnalyzer

def diagnostic_distances():
    """Diagnostic des distances entre magasins et concurrents"""
    
    # Chargement des données
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data')
    
    magasins = pd.read_csv(os.path.join(data_path, 'magasins_performance.csv'))
    concurrents = pd.read_csv(os.path.join(data_path, 'sites_concurrents.csv'))
    
    print("🔍 DIAGNOSTIC DES DISTANCES")
    print("="*50)
    
    # Analyse des premiers concurrents
    for i in range(min(5, len(concurrents))):
        concurrent = concurrents.iloc[i]
        concurrent_coords = (concurrent['latitude'], concurrent['longitude'])
        
        print(f"\n📍 {concurrent['id_site']} - {concurrent['type_concurrent']}")
        print(f"   Zone de chalandise: {concurrent['zone_chalandise_km']}km")
        print(f"   Position: {concurrent['latitude']:.2f}, {concurrent['longitude']:.2f}")
        
        # Calcul des distances vers tous les magasins
        distances = []
        for _, magasin in magasins.iterrows():
            magasin_coords = (magasin['latitude'], magasin['longitude'])
            distance = geodesic(concurrent_coords, magasin_coords).kilometers
            distances.append({
                'magasin': magasin['id_magasin'],
                'ville': magasin['ville'],
                'distance_km': distance,
                'dans_zone': distance <= concurrent['zone_chalandise_km']
            })
        
        # Tri par distance
        distances_df = pd.DataFrame(distances).sort_values('distance_km')
        
        # Magasins les plus proches
        print("   🏪 5 magasins les plus proches:")
        for _, row in distances_df.head(5).iterrows():
            status = "✅ DANS ZONE" if row['dans_zone'] else "❌ Hors zone"
            print(f"      {row['magasin']} ({row['ville']}): {row['distance_km']:.1f}km - {status}")
        
        # Statistiques
        dans_zone = distances_df[distances_df['dans_zone'] == True]
        print(f"   📊 Magasins dans la zone: {len(dans_zone)}/{len(distances_df)}")
        print(f"   📏 Distance minimale: {distances_df['distance_km'].min():.1f}km")

def test_avec_zone_elargie():
    """Test avec des zones de chalandise élargies"""
    
    print("\n\n🔧 TEST AVEC ZONES ÉLARGIES")
    print("="*50)
    
    # Chargement des données
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data')
    
    magasins = pd.read_csv(os.path.join(data_path, 'magasins_performance.csv'))
    concurrents = pd.read_csv(os.path.join(data_path, 'sites_concurrents.csv'))
    
    # Modification temporaire des zones de chalandise
    concurrents_test = concurrents.copy()
    concurrents_test['zone_chalandise_km'] = concurrents_test['zone_chalandise_km'] * 2  # Doubler les zones
    
    # Test avec SITE_001
    analyzer = CompetitiveImpactAnalyzer(magasins, concurrents_test)
    
    print("📍 Test avec SITE_001 (zone élargie)")
    impacts = analyzer.analyze_scenario('SITE_001')
    
    if impacts is not None:
        magasins_impactes = impacts[impacts['dans_zone'] == True]
        print(f"✅ Magasins impactés avec zone élargie: {len(magasins_impactes)}")
    else:
        print("❌ Toujours aucun impact")

def proposer_solutions():
    """Propose des solutions pour améliorer l'analyse"""
    
    print("\n\n💡 SOLUTIONS PROPOSÉES")
    print("="*50)
    
    print("1. 🎯 Ajuster les zones de chalandise:")
    print("   - Zones actuelles trop petites par rapport aux distances")
    print("   - Augmenter les zones ou repositionner les concurrents")
    
    print("\n2. 📍 Repositionner les concurrents:")
    print("   - Placer des concurrents près des grandes villes")
    print("   - Utiliser des coordonnées réalistes")
    
    print("\n3. ⚙️ Ajuster le modèle d'impact:")
    print("   - Réduire le seuil d'impact minimum")
    print("   - Augmenter la portée d'influence")

if __name__ == "__main__":
    diagnostic_distances()
    test_avec_zone_elargie()
    proposer_solutions()