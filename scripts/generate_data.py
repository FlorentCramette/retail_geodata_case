"""
Générateur de données retail géolocalisées
Simule des magasins avec performances et variables géodémographiques
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Configuration
np.random.seed(42)
random.seed(42)

def generate_retail_data():
    """Génère un dataset réaliste de magasins avec géolocalisation"""
    
    # Villes françaises avec coordonnées approximatives
    cities_data = [
        {'ville': 'Lyon', 'lat': 45.7640, 'lon': 4.8357, 'population': 515695, 'densite': 10476},
        {'ville': 'Marseille', 'lat': 43.2965, 'lon': 5.3698, 'population': 870731, 'densite': 3634},
        {'ville': 'Toulouse', 'lat': 43.6047, 'lon': 1.4442, 'population': 479553, 'densite': 4093},
        {'ville': 'Nice', 'lat': 43.7102, 'lon': 7.2620, 'population': 343304, 'densite': 4794},
        {'ville': 'Nantes', 'lat': 47.2184, 'lon': -1.5536, 'population': 314138, 'densite': 4826},
        {'ville': 'Montpellier', 'lat': 43.6119, 'lon': 3.8772, 'population': 295542, 'densite': 5096},
        {'ville': 'Strasbourg', 'lat': 48.5734, 'lon': 7.7521, 'population': 284677, 'densite': 3666},
        {'ville': 'Bordeaux', 'lat': 44.8378, 'lon': -0.5792, 'population': 260958, 'densite': 5196},
        {'ville': 'Lille', 'lat': 50.6292, 'lon': 3.0573, 'population': 234475, 'densite': 6917},
        {'ville': 'Rennes', 'lat': 48.1173, 'lon': -1.6778, 'population': 220488, 'densite': 4293}
    ]
    
    # Types d'enseignes
    enseignes = ['SuperFrais', 'MarchéPlus', 'BioNature', 'CityMarket', 'FamilyShop']
    formats = ['Hypermarché', 'Supermarché', 'Proximité', 'Drive', 'Express']
    
    magasins = []
    
    for i in range(50):  # 50 magasins
        city = random.choice(cities_data)
        
        # Position avec variabilité autour de la ville
        lat_var = np.random.normal(0, 0.05)  # ~5km de variabilité
        lon_var = np.random.normal(0, 0.05)
        
        # Variables démographiques influençant le CA
        population_zone = max(5000, int(np.random.normal(city['population']/10, city['population']/20)))
        densite = max(500, int(np.random.normal(city['densite'], city['densite']*0.3)))
        revenu_median = np.random.normal(28000, 8000)  # Revenu médian zone
        concurrents_500m = np.random.poisson(2)  # Nombre concurrents dans 500m
        parking_places = np.random.randint(50, 500)
        
        # Variables d'accessibilité
        distance_centre = abs(np.random.normal(3, 2))  # km du centre-ville
        transport_score = np.random.randint(1, 10)  # Score accessibilité transports
        
        # CA influencé par ces variables (modèle réaliste)
        ca_base = (
            population_zone * 0.8 +  # Plus de population = plus de CA
            revenu_median * 15 +     # Plus de revenu = plus de dépenses
            parking_places * 800 +   # Plus de parking = plus de CA
            transport_score * 50000 - # Meilleur transport = plus de CA
            concurrents_500m * 200000 - # Plus de concurrents = moins de CA
            distance_centre * 30000   # Plus loin du centre = moins de CA
        )
        
        # Ajout de bruit réaliste
        ca_annuel = max(500000, int(ca_base * np.random.normal(1, 0.2)))
        
        # Métriques dérivées
        nb_clients_mois = int(ca_annuel / (np.random.normal(45, 10) * 12))  # Panier moyen ~45€
        panier_moyen = ca_annuel / (nb_clients_mois * 12)
        
        # Surface et effectif corrélés au CA
        surface = max(200, int(ca_annuel / np.random.normal(15000, 3000)))  # €/m²
        effectif = max(5, int(surface / np.random.normal(25, 5)))  # m²/employé
        
        magasin = {
            'id_magasin': f'MAG_{i+1:03d}',
            'enseigne': random.choice(enseignes),
            'format': random.choice(formats),
            'ville': city['ville'],
            'latitude': round(city['lat'] + lat_var, 6),
            'longitude': round(city['lon'] + lon_var, 6),
            'date_ouverture': datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1460)),
            
            # Variables de performance
            'ca_annuel': ca_annuel,
            'nb_clients_mois': nb_clients_mois,
            'panier_moyen': round(panier_moyen, 2),
            'surface_vente': surface,
            'effectif': effectif,
            
            # Variables géodémographiques
            'population_zone_1km': population_zone,
            'densite_hab_km2': densite,
            'revenu_median_zone': round(revenu_median),
            'age_moyen_zone': round(np.random.normal(40, 8), 1),
            
            # Variables concurrentielles
            'concurrents_500m': concurrents_500m,
            'concurrents_1km': concurrents_500m + np.random.poisson(3),
            
            # Variables d'accessibilité
            'parking_places': parking_places,
            'distance_centre_ville': round(distance_centre, 1),
            'transport_score': transport_score,
            'zone_commerciale': random.choice([True, False]),
            
            # Variables temporelles
            'mois': random.randint(1, 12),
            'trimestre': np.random.choice(['T1', 'T2', 'T3', 'T4'])
        }
        
        magasins.append(magasin)
    
    return pd.DataFrame(magasins)

def generate_concurrent_data():
    """Génère des données de concurrents potentiels"""
    
    sites_potentiels = []
    
    for i in range(20):
        # Nouvelles implantations potentielles
        lat = np.random.uniform(43.0, 50.0)  # France métropolitaine
        lon = np.random.uniform(-4.0, 8.0)
        
        site = {
            'id_site': f'SITE_{i+1:03d}',
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'type_concurrent': random.choice(['Hypermarché', 'Supermarché', 'Drive', 'Discount']),
            'enseigne_concurrent': random.choice(['Concur1', 'Concur2', 'Concur3']),
            'surface_prevue': np.random.randint(800, 3000),
            'ouverture_prevue': datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365)),
            'investissement': np.random.randint(2, 8) * 1000000,  # 2-8M€
            'zone_chalandise_km': round(np.random.uniform(2, 8), 1)
        }
        sites_potentiels.append(site)
    
    return pd.DataFrame(sites_potentiels)

if __name__ == "__main__":
    # Génération des données
    print("Génération des données magasins...")
    df_magasins = generate_retail_data()
    
    print("Génération des données concurrents...")
    df_concurrents = generate_concurrent_data()
    
    # Sauvegarde
    df_magasins.to_csv('../data/magasins_performance.csv', index=False)
    df_concurrents.to_csv('../data/sites_concurrents.csv', index=False)
    
    print(f"✅ Données générées:")
    print(f"   - {len(df_magasins)} magasins sauvegardés")
    print(f"   - {len(df_concurrents)} sites concurrents potentiels")
    print(f"   - CA moyen: {df_magasins['ca_annuel'].mean():,.0f}€")
    print(f"   - Panier moyen: {df_magasins['panier_moyen'].mean():.2f}€")