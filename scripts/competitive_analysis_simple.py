"""
Version simplifiée de l'analyseur d'impact concurrentiel
"""

import pandas as pd
import numpy as np
try:
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    # Fonction de fallback pour calculer la distance
    def geodesic(coord1, coord2):
        # Distance euclidienne approximative
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        return type('Distance', (), {'km': np.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 111})()

class CompetitiveImpactAnalyzer:
    """Analyseur d'impact concurrentiel - Version simplifiée"""
    
    def __init__(self, magasins_df=None, concurrents_df=None):
        self.magasins = magasins_df if magasins_df is not None else self._create_demo_data()
        self.concurrents = concurrents_df if concurrents_df is not None else self._create_demo_competitors()
        
    def _create_demo_data(self):
        """Crée des données de démonstration"""
        return pd.DataFrame({
            'id_magasin': ['MAG_001', 'MAG_002', 'MAG_003'],
            'nom_magasin': ['Super Lyon', 'Hyper Paris', 'Market Nice'],
            'latitude': [45.764, 48.856, 43.710],
            'longitude': [4.835, 2.352, 7.262],
            'ca_annuel': [850000, 1200000, 600000],
            'surface_vente': [1200, 1800, 900]
        })
    
    def _create_demo_competitors(self):
        """Crée des données de concurrents de démonstration"""
        return pd.DataFrame({
            'id_concurrent': ['CONC_001', 'CONC_002'],
            'nom_concurrent': ['Nouveau Super', 'Mega Store'],
            'latitude': [45.770, 48.860],
            'longitude': [4.840, 2.355],
            'surface_prevue': [1500, 2000],
            'type_concurrent': ['Supermarché', 'Hypermarché']
        })
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calcule la distance entre deux points"""
        try:
            coord1 = (lat1, lon1)
            coord2 = (lat2, lon2)
            distance = geodesic(coord1, coord2).km
            return distance
        except Exception as e:
            # Distance euclidienne de fallback
            return np.sqrt((lat2-lat1)**2 + (lon2-lon1)**2) * 111
    
    def analyze_impact(self, concurrent_id, rayon_impact=5.0):
        """Analyse l'impact d'un concurrent sur les magasins"""
        try:
            if concurrent_id not in self.concurrents['id_concurrent'].values:
                return {
                    'concurrent_id': concurrent_id,
                    'magasins_impactes': [],
                    'impact_total': 0,
                    'nombre_magasins_impactes': 0,
                    'error': 'Concurrent non trouvé'
                }
            
            concurrent = self.concurrents[self.concurrents['id_concurrent'] == concurrent_id].iloc[0]
            lat_conc = concurrent['latitude']
            lon_conc = concurrent['longitude']
            
            impacts = []
            
            for _, magasin in self.magasins.iterrows():
                distance = self.calculate_distance(
                    magasin['latitude'], magasin['longitude'],
                    lat_conc, lon_conc
                )
                
                if distance <= rayon_impact:
                    # Calcul d'impact simple basé sur la distance
                    impact_pct = max(0, (rayon_impact - distance) / rayon_impact * 0.15)  # Max 15% d'impact
                    impact_ca = magasin['ca_annuel'] * impact_pct
                    
                    impacts.append({
                        'id_magasin': magasin['id_magasin'],
                        'nom_magasin': magasin['nom_magasin'],
                        'distance_km': round(distance, 2),
                        'impact_pct': round(impact_pct * 100, 1),
                        'impact_ca_euro': round(impact_ca, 0),
                        'ca_actuel': magasin['ca_annuel']
                    })
            
            impact_total = sum([imp['impact_ca_euro'] for imp in impacts])
            
            return {
                'concurrent_id': concurrent_id,
                'concurrent_nom': concurrent['nom_concurrent'],
                'magasins_impactes': impacts,
                'impact_total': impact_total,
                'nombre_magasins_impactes': len(impacts),
                'rayon_analyse': rayon_impact
            }
            
        except Exception as e:
            return {
                'concurrent_id': concurrent_id,
                'magasins_impactes': [],
                'impact_total': 0,
                'nombre_magasins_impactes': 0,
                'error': str(e)
            }
    
    def get_zones_impact(self, rayon=5.0):
        """Calcule les zones d'impact pour tous les concurrents"""
        zones = []
        
        for _, concurrent in self.concurrents.iterrows():
            zone = {
                'id': concurrent['id_concurrent'],
                'nom': concurrent['nom_concurrent'],
                'latitude': concurrent['latitude'],
                'longitude': concurrent['longitude'],
                'rayon': rayon,
                'type': concurrent.get('type_concurrent', 'Concurrent')
            }
            zones.append(zone)
        
        return zones
    
    def get_summary_stats(self):
        """Statistiques de résumé"""
        try:
            total_magasins = len(self.magasins)
            total_concurrents = len(self.concurrents)
            ca_total = self.magasins['ca_annuel'].sum() if 'ca_annuel' in self.magasins.columns else 0
            
            return {
                'total_magasins': total_magasins,
                'total_concurrents': total_concurrents,
                'ca_total_reseau': ca_total,
                'ca_moyen_magasin': ca_total / total_magasins if total_magasins > 0 else 0,
                'geopy_available': GEOPY_AVAILABLE
            }
        except Exception as e:
            return {
                'total_magasins': 0,
                'total_concurrents': 0,
                'ca_total_reseau': 0,
                'ca_moyen_magasin': 0,
                'error': str(e),
                'geopy_available': GEOPY_AVAILABLE
            }


# Test du module si exécuté directement
if __name__ == "__main__":
    print("🧪 Test du module CompetitiveImpactAnalyzer simplifié")
    
    analyzer = CompetitiveImpactAnalyzer()
    
    # Test des statistiques
    stats = analyzer.get_summary_stats()
    print(f"✅ Magasins: {stats['total_magasins']}, Concurrents: {stats['total_concurrents']}")
    print(f"✅ Geopy disponible: {stats['geopy_available']}")
    
    # Test d'analyse d'impact
    if len(analyzer.concurrents) > 0:
        premier_concurrent = analyzer.concurrents.iloc[0]['id_concurrent']
        impact = analyzer.analyze_impact(premier_concurrent)
        print(f"✅ Analyse d'impact: {impact['nombre_magasins_impactes']} magasins impactés")
        print(f"✅ Impact total: {impact['impact_total']:,.0f}€")
