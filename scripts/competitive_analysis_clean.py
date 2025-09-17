"""
Analyse d'impact concurrentiel
Simulation de l'effet d'ouverture de nouveaux concurrents
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium import plugins
from geopy.distance import geodesic
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CompetitiveImpactAnalyzer:
    """Analyseur d'impact concurrentiel"""
    
    def __init__(self, magasins_df, concurrents_df):
        self.magasins = magasins_df.copy()
        self.concurrents = concurrents_df.copy()
        self.impact_results = {}
    
    def calculate_distance_matrix(self):
        """Calcule la matrice des distances entre magasins et concurrents"""
        
        distances = []
        
        for _, magasin in self.magasins.iterrows():
            mag_coords = (magasin['latitude'], magasin['longitude'])
            
            for _, concurrent in self.concurrents.iterrows():
                conc_coords = (concurrent['latitude'], concurrent['longitude'])
                
                distance_km = geodesic(mag_coords, conc_coords).kilometers
                
                distances.append({
                    'id_magasin': magasin['id_magasin'],
                    'id_concurrent': concurrent['id_site'],
                    'distance_km': distance_km,
                    'magasin_ca': magasin['ca_annuel'],
                    'magasin_ville': magasin['ville'],
                    'concurrent_type': concurrent['type_concurrent'],
                    'concurrent_surface': concurrent['surface_prevue'],
                    'zone_chalandise': concurrent['zone_chalandise_km']
                })
        
        return pd.DataFrame(distances)
    
    def estimate_impact_by_distance(self, distance_matrix):
        """Estime l'impact selon la distance et la zone de chalandise"""
        
        # Modèle d'impact basé sur la distance et la taille du concurrent
        def calculate_impact(row):
            distance = row['distance_km']
            zone_chalandise = row['zone_chalandise']
            surface_concurrent = row['concurrent_surface']
            ca_actuel = row['magasin_ca']
            
            # Impact maximal si dans la zone de chalandise
            if distance <= zone_chalandise:
                # Impact proportionnel à la surface du concurrent
                impact_base = min(0.25, surface_concurrent / 5000)  # Max 25% impact
                
                # Facteur distance (plus proche = plus d'impact)
                distance_factor = max(0.1, 1 - (distance / zone_chalandise))
                
                # Impact final
                impact_percent = impact_base * distance_factor
                
                # Perte de CA estimée
                perte_ca = ca_actuel * impact_percent
                
                return {
                    'impact_percent': impact_percent,
                    'perte_ca_estimee': perte_ca,
                    'dans_zone': True
                }
            else:
                return {
                    'impact_percent': 0,
                    'perte_ca_estimee': 0,
                    'dans_zone': False
                }
        
        # Application du calcul d'impact
        impacts = distance_matrix.apply(calculate_impact, axis=1, result_type='expand')
        
        # Fusion avec la matrice de distance
        result = pd.concat([distance_matrix, impacts], axis=1)
        
        return result
    
    def analyze_scenario(self, concurrent_id):
        """Analyse l'impact d'un concurrent spécifique"""
        
        print(f"🎯 Analyse d'impact - Concurrent {concurrent_id}")
        print("="*50)
        
        # Calcul des distances
        distance_matrix = self.calculate_distance_matrix()
        
        # Filtrage pour le concurrent analysé
        concurrent_data = distance_matrix[distance_matrix['id_concurrent'] == concurrent_id]
        
        # Calcul des impacts
        impacts = self.estimate_impact_by_distance(concurrent_data)
        
        # Magasins impactés
        magasins_impactes = impacts[impacts['dans_zone'] == True]
        
        if len(magasins_impactes) == 0:
            print("✅ Aucun magasin impacté par ce concurrent")
            return None
        
        # Statistiques d'impact
        nb_impactes = len(magasins_impactes)
        perte_totale = magasins_impactes['perte_ca_estimee'].sum()
        impact_moyen = magasins_impactes['impact_percent'].mean()
        
        print(f"📊 Résultats:")
        print(f"   • Magasins impactés: {nb_impactes}")
        print(f"   • Perte de CA totale: {perte_totale:,.0f}€")
        print(f"   • Impact moyen: {impact_moyen:.1%}")
        
        # Détail par magasin
        print(f"\n🏪 Détail par magasin:")
        detail = magasins_impactes[[
            'id_magasin', 'magasin_ville', 'distance_km', 
            'impact_percent', 'perte_ca_estimee'
        ]].sort_values('perte_ca_estimee', ascending=False)
        
        for _, row in detail.iterrows():
            print(f"   • {row['id_magasin']} ({row['magasin_ville']}): ")
            print(f"     Distance: {row['distance_km']:.1f}km, ")
            print(f"     Impact: {row['impact_percent']:.1%}, ")
            print(f"     Perte: {row['perte_ca_estimee']:,.0f}€")
        
        self.impact_results[concurrent_id] = {
            'impacts': impacts,
            'magasins_impactes': magasins_impactes,
            'perte_totale': perte_totale,
            'nb_impactes': nb_impactes
        }
        
        return impacts
    
    def compare_scenarios(self):
        """Compare l'impact de tous les concurrents"""
        
        print("📊 COMPARAISON DES SCÉNARIOS")
        print("="*50)
        
        if not self.impact_results:
            print("❌ Aucune analyse d'impact disponible")
            return None
        
        # Compilation des résultats
        comparison_data = []
        
        for concurrent_id, results in self.impact_results.items():
            concurrent_info = self.concurrents[self.concurrents['id_site'] == concurrent_id].iloc[0]
            
            comparison_data.append({
                'concurrent_id': concurrent_id,
                'type': concurrent_info['type_concurrent'],
                'surface': concurrent_info['surface_prevue'],
                'zone_chalandise': concurrent_info['zone_chalandise_km'],
                'magasins_impactes': results['nb_impactes'],
                'perte_totale': results['perte_totale']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('perte_totale', ascending=False)
        
        print("🎯 Ranking des menaces:")
        for i, row in comparison_df.iterrows():
            print(f"{i + 1}. {row['concurrent_id']} ({row['type']})")
            print(f"   Perte estimée: {row['perte_totale']:,.0f}€")
            print(f"   Magasins impactés: {row['magasins_impactes']}")
            print()
        
        return comparison_df
    
    def generate_report(self, output_file='../data/rapport_impact_concurrentiel.txt'):
        """Génère un rapport d'analyse"""
        
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("RAPPORT D'ANALYSE CONCURRENTIELLE\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"Date d'analyse: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Nombre de magasins analysés: {len(self.magasins)}\n")
            f.write(f"Nombre de concurrents évalués: {len(self.concurrents)}\n\n")
            
            # Résumé par concurrent
            for concurrent_id, results in self.impact_results.items():
                concurrent_info = self.concurrents[self.concurrents['id_site'] == concurrent_id].iloc[0]
                
                f.write(f"CONCURRENT: {concurrent_id}\n")
                f.write(f"Type: {concurrent_info['type_concurrent']}\n")
                f.write(f"Surface: {concurrent_info['surface_prevue']}m²\n")
                f.write(f"Zone de chalandise: {concurrent_info['zone_chalandise_km']}km\n")
                f.write(f"Magasins impactés: {results['nb_impactes']}\n")
                f.write(f"Perte totale estimée: {results['perte_totale']:,.0f}€\n")
                f.write("-" * 30 + "\n\n")
        
        print(f"✅ Rapport généré: {output_file}")


def demo_competitive_analysis():
    """Démonstration de l'analyse concurrentielle"""
    
    print("🔍 DÉMONSTRATION - Analyse d'impact concurrentiel")
    print("="*60)
    
    # Chargement des données avec chemin correct
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data')
    
    magasins = pd.read_csv(os.path.join(data_path, 'magasins_performance.csv'))
    concurrents = pd.read_csv(os.path.join(data_path, 'sites_concurrents.csv'))
    
    print(f"📊 Données chargées:")
    print(f"   • {len(magasins)} magasins")
    print(f"   • {len(concurrents)} sites concurrents")
    
    # Initialisation de l'analyseur
    analyzer = CompetitiveImpactAnalyzer(magasins, concurrents)
    
    # Analyse des 3 premiers concurrents
    for i in range(min(3, len(concurrents))):
        concurrent_id = concurrents.iloc[i]['id_site']
        print(f"\n📍 Analyse du concurrent {concurrent_id}")
        analyzer.analyze_scenario(concurrent_id)
        print("\n" + "-"*50)
    
    # Comparaison des scénarios
    print("\n")
    comparison = analyzer.compare_scenarios()
    
    # Génération du rapport
    analyzer.generate_report()
    
    return analyzer


if __name__ == "__main__":
    analyzer = demo_competitive_analysis()