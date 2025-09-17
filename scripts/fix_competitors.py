"""
Correction des données concurrentielles
Repositionnement des concurrents près des magasins pour des analyses réalistes
"""

import pandas as pd
import numpy as np
from geopy.distance import geodesic
import random

def generer_concurrents_realistes():
    """Génère des concurrents positionnés près des magasins existants"""
    
    # Chargement des magasins avec chemin correct
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data')
    
    magasins = pd.read_csv(os.path.join(data_path, 'magasins_performance.csv'))
    
    # Extraction des villes principales
    villes_principales = magasins.groupby('ville').agg({
        'latitude': 'mean',
        'longitude': 'mean',
        'ca_annuel': 'count'
    }).reset_index()
    villes_principales = villes_principales.rename(columns={'ca_annuel': 'nb_magasins'})
    
    print("🏙️ Villes principales avec magasins:")
    print(villes_principales)
    
    concurrents_data = []
    concurrent_id = 1
    
    for _, ville in villes_principales.iterrows():
        # Nombre de concurrents par ville proportionnel au nombre de magasins
        nb_concurrents = max(1, ville['nb_magasins'] // 3)
        
        for i in range(nb_concurrents):
            # Position aléatoire dans un rayon de 15km autour du centre ville
            angle = random.uniform(0, 2 * np.pi)
            distance_km = random.uniform(2, 15)  # Entre 2 et 15km du centre
            
            # Calcul des nouvelles coordonnées
            lat_offset = (distance_km / 111) * np.cos(angle)  # 1 degré ≈ 111km
            lon_offset = (distance_km / (111 * np.cos(np.radians(ville['latitude'])))) * np.sin(angle)
            
            nouvelle_lat = ville['latitude'] + lat_offset
            nouvelle_lon = ville['longitude'] + lon_offset
            
            # Types de concurrents
            types_concurrents = ['Hypermarché', 'Supermarché', 'Discount', 'Drive']
            enseignes_concur = ['Concur1', 'Concur2', 'Concur3']
            
            # Caractéristiques aléatoires
            type_concurrent = random.choice(types_concurrents)
            surface = random.randint(800, 3000)
            zone_chalandise = random.uniform(3, 12)  # Zones plus larges
            
            concurrents_data.append({
                'id_site': f'SITE_{concurrent_id:03d}',
                'latitude': nouvelle_lat,
                'longitude': nouvelle_lon,
                'type_concurrent': type_concurrent,
                'enseigne_concurrent': random.choice(enseignes_concur),
                'surface_prevue': surface,
                'ouverture_prevue': f'2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                'investissement': random.randint(2, 8) * 1000000,
                'zone_chalandise_km': zone_chalandise,
                'ville_proche': ville['ville']
            })
            
            concurrent_id += 1
    
    # Création du DataFrame
    concurrents_df = pd.DataFrame(concurrents_data)
    
    # Sauvegarde avec chemin correct
    output_path = os.path.join(data_path, 'sites_concurrents.csv')
    concurrents_df.to_csv(output_path, index=False)
    
    print(f"\n✅ {len(concurrents_df)} concurrents générés")
    print(f"Répartition par ville: {concurrents_df['ville_proche'].value_counts().to_dict()}")
    print(f"Fichier sauvegardé : {output_path}")
    
    return concurrents_df

def valider_distances(magasins, concurrents):
    """Valide que les concurrents sont bien positionnés"""
    
    print("\n🔍 VALIDATION DES DISTANCES")
    print("="*50)
    
    for i, concurrent in concurrents.head(5).iterrows():
        concurrent_coords = (concurrent['latitude'], concurrent['longitude'])
        
        # Distances vers les magasins de la même ville
        magasins_ville = magasins[magasins['ville'] == concurrent['ville_proche']]
        
        if len(magasins_ville) > 0:
            distances = []
            for _, magasin in magasins_ville.iterrows():
                magasin_coords = (magasin['latitude'], magasin['longitude'])
                distance = geodesic(concurrent_coords, magasin_coords).kilometers
                distances.append(distance)
            
            min_distance = min(distances)
            dans_zone = min_distance <= concurrent['zone_chalandise_km']
            
            print(f"📍 {concurrent['id_site']} ({concurrent['ville_proche']})")
            print(f"   Zone: {concurrent['zone_chalandise_km']:.1f}km")
            print(f"   Distance min: {min_distance:.1f}km")
            print(f"   Impact: {'✅ OUI' if dans_zone else '❌ NON'}")

if __name__ == "__main__":
    # Génération des nouveaux concurrents
    concurrents_realistes = generer_concurrents_realistes()
    
    # Validation des résultats
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data')
    
    magasins = pd.read_csv(os.path.join(data_path, 'magasins_performance.csv'))
    valider_distances(magasins, concurrents_realistes)
    
    print("\n🎯 Les concurrents sont maintenant positionnés de manière réaliste !")
    print("Relancez le dashboard pour tester l'analyse d'impact.")