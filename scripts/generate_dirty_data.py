"""
Générateur de données 'sales' pour simuler un pipeline de données réaliste
Crée des fichiers CSV avec les problèmes typiques rencontrés en production :
- Cellules vides et valeurs nulles
- Formats incohérents  
- Doublons partiels
- Erreurs de saisie
- Encodage mixte
- Colonnes manquantes
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

class DirtyDataGenerator:
    """Générateur de données sales pour simulation pipeline"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
        # Définir les chemins de sortie
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.current_dir)
        self.raw_data_path = os.path.join(self.project_root, 'data', 'raw')
        
        # Données de référence pour générer des erreurs réalistes
        self.villes_typos = {
            'Paris': ['paris', 'PARIS', 'Pars', 'Paaris', '  Paris  '],
            'Lyon': ['lyon', 'LYON', 'Lyonn', 'Llyon', 'Lyon '],
            'Marseille': ['marseille', 'MARSEILLE', 'Marsseille', 'Marceille'],
            'Toulouse': ['toulouse', 'TOULOUSE', 'Touluse', 'Tpulouse'],
            'Nice': ['nice', 'NICE', 'Niice', 'Nise'],
            'Nantes': ['nantes', 'NANTES', 'Nantess', 'Nantes  '],
            'Bordeaux': ['bordeaux', 'BORDEAUX', 'Bordiaux', 'Bordeau'],
            'Lille': ['lille', 'LILLE', 'Lile', 'Lillle', 'L ille'],
            'Strasbourg': ['strasbourg', 'STRASBOURG', 'Strabourg', 'Straborg'],
            'Montpellier': ['montpellier', 'MONTPELLIER', 'Montpelier', 'Montpelllier']
        }
        
        self.formats_date = [
            '%Y-%m-%d',  # Standard
            '%d/%m/%Y',  # Français
            '%m/%d/%Y',  # Américain
            '%d-%m-%Y',  # Alternatif
            '%Y/%m/%d'   # ISO alternatif
        ]
        
    def introduce_nulls(self, series: pd.Series, null_rate: float = 0.1) -> pd.Series:
        """Introduit des valeurs nulles aléatoires"""
        mask = np.random.random(len(series)) < null_rate
        result = series.copy()
        
        # Différents types de valeurs nulles
        null_values = [None, np.nan, '', '  ', 'NULL', 'null', 'N/A', 'n/a', '#N/A']
        
        for i in range(len(result)):
            if mask[i]:
                result.iloc[i] = random.choice(null_values)
        
        return result
    
    def introduce_typos(self, series: pd.Series, error_rate: float = 0.05) -> pd.Series:
        """Introduit des erreurs de frappe"""
        result = series.copy()
        
        for i in range(len(result)):
            if np.random.random() < error_rate and pd.notna(result.iloc[i]):
                value = str(result.iloc[i])
                
                # Types d'erreurs
                error_type = random.choice(['char_swap', 'extra_char', 'missing_char', 'case_mix'])
                
                if error_type == 'char_swap' and len(value) > 1:
                    # Échange de caractères
                    pos = random.randint(0, len(value) - 2)
                    value_list = list(value)
                    value_list[pos], value_list[pos + 1] = value_list[pos + 1], value_list[pos]
                    result.iloc[i] = ''.join(value_list)
                    
                elif error_type == 'extra_char':
                    # Caractère en trop
                    pos = random.randint(0, len(value))
                    char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    result.iloc[i] = value[:pos] + char + value[pos:]
                    
                elif error_type == 'missing_char' and len(value) > 1:
                    # Caractère manquant
                    pos = random.randint(0, len(value) - 1)
                    result.iloc[i] = value[:pos] + value[pos + 1:]
                    
                elif error_type == 'case_mix':
                    # Casse mélangée
                    result.iloc[i] = ''.join(random.choice([c.upper(), c.lower()]) for c in value)
        
        return result
    
    def introduce_city_errors(self, series: pd.Series) -> pd.Series:
        """Introduit des erreurs spécifiques aux noms de villes"""
        result = series.copy()
        
        for i in range(len(result)):
            if pd.notna(result.iloc[i]):
                city = str(result.iloc[i])
                
                # Utiliser les variantes d'erreurs prédéfinies
                for correct_city, variants in self.villes_typos.items():
                    if city == correct_city and np.random.random() < 0.1:
                        result.iloc[i] = random.choice(variants)
                        break
        
        return result
    
    def introduce_date_format_inconsistency(self, dates: List[datetime]) -> List[str]:
        """Introduit des formats de date incohérents"""
        result = []
        
        for date in dates:
            if pd.isna(date):
                result.append('')
                continue
                
            # Choix aléatoire du format
            format_choice = random.choice(self.formats_date)
            
            try:
                # Parfois introduire des erreurs
                if np.random.random() < 0.05:
                    # Date invalide
                    result.append(random.choice(['32/13/2023', '00/00/0000', '2023-13-45', '31/02/2023']))
                else:
                    result.append(date.strftime(format_choice))
            except:
                result.append('')
        
        return result
    
    def create_dirty_magasins_data(self) -> pd.DataFrame:
        """Crée des données sales pour les magasins"""
        print("🏪 Génération des données sales - Magasins...")
        
        # Charger les données propres comme base
        clean_data_path = os.path.join(self.project_root, 'data', 'magasins_performance.csv')
        df_clean = pd.read_csv(clean_data_path)
        
        # Créer une version "sale"
        df_dirty = df_clean.copy()
        
        # 1. Introduire des valeurs nulles
        df_dirty['ville'] = self.introduce_nulls(df_dirty['ville'], 0.08)
        df_dirty['population_zone_1km'] = self.introduce_nulls(df_dirty['population_zone_1km'], 0.05)
        df_dirty['ca_annuel'] = self.introduce_nulls(df_dirty['ca_annuel'], 0.03)
        
        # 2. Erreurs de frappe sur les villes
        df_dirty['ville'] = self.introduce_city_errors(df_dirty['ville'])
        df_dirty['ville'] = self.introduce_typos(df_dirty['ville'], 0.1)
        
        # 3. Formats incohérents pour les coordonnées
        for i in range(len(df_dirty)):
            if np.random.random() < 0.05:
                # Parfois utiliser des virgules au lieu de points
                df_dirty.loc[i, 'latitude'] = str(df_dirty.loc[i, 'latitude']).replace('.', ',')
                df_dirty.loc[i, 'longitude'] = str(df_dirty.loc[i, 'longitude']).replace('.', ',')
        
        # 4. Ajouter des colonnes avec des erreurs
        # Dates d'ouverture avec formats incohérents
        base_date = datetime(2020, 1, 1)
        dates = [base_date + timedelta(days=random.randint(0, 1000)) for _ in range(len(df_dirty))]
        df_dirty['date_ouverture'] = self.introduce_date_format_inconsistency(dates)
        
        # 5. Doublons partiels (mêmes coordonnées, noms légèrement différents)
        for i in range(3):  # Créer quelques doublons
            if i < len(df_dirty) - 1:
                # Dupliquer une ligne avec de légères variations
                dup_idx = len(df_dirty)
                df_dirty.loc[dup_idx] = df_dirty.iloc[i].copy()
                df_dirty.loc[dup_idx, 'magasin_id'] = f"MAG_{dup_idx:03d}_DUP"
                df_dirty.loc[dup_idx, 'ville'] = str(df_dirty.loc[dup_idx, 'ville']) + " "
        
        # 6. Valeurs aberrantes
        for i in range(len(df_dirty)):
            if np.random.random() < 0.02:
                # CA aberrant
                df_dirty.loc[i, 'ca_annuel'] = df_dirty.loc[i, 'ca_annuel'] * random.choice([0.01, 100, 1000])
            if np.random.random() < 0.01:
                # Population aberrante
                df_dirty.loc[i, 'population_zone_1km'] = -random.randint(1000, 50000)
        
        # 7. Espaces indésirables
        for col in df_dirty.select_dtypes(include=['object']).columns:
            df_dirty[col] = df_dirty[col].astype(str).apply(
                lambda x: '  ' + x + '  ' if pd.notna(x) and np.random.random() < 0.1 else x
            )
        
        return df_dirty
    
    def create_dirty_competitors_data(self) -> pd.DataFrame:
        """Crée des données sales pour les concurrents"""
        print("🏢 Génération des données sales - Concurrents...")
        
        # Charger les données propres
        clean_data_path = os.path.join(self.project_root, 'data', 'sites_concurrents.csv')
        df_clean = pd.read_csv(clean_data_path)
        
        df_dirty = df_clean.copy()
        
        # Problèmes spécifiques aux concurrents
        # 1. Types de magasins avec erreurs
        df_dirty['type_concurrent'] = self.introduce_typos(df_dirty['type_concurrent'], 0.15)
        
        # 2. Noms d'enseignes avec variantes
        enseignes_variants = {
            'Carrefour': ['carrefour', 'CARREFOUR', 'Carefour', 'Carfour'],
            'Leclerc': ['leclerc', 'LECLERC', 'LeClerc', 'Le Clerc'],
            'Auchan': ['auchan', 'AUCHAN', 'Auchant', 'Aushan'],
            'Intermarché': ['intermarche', 'INTERMARCHE', 'Inter marché', 'Intermarche']
        }
        
        # Ajouter une colonne enseigne avec erreurs (utiliser la colonne existante)
        df_dirty['enseigne_concurrent'] = self.introduce_typos(df_dirty['enseigne_concurrent'], 0.15)
        
        # Introduire des variantes d'enseignes
        for i in range(len(df_dirty)):
            if pd.notna(df_dirty.loc[i, 'enseigne_concurrent']) and np.random.random() < 0.2:
                current_enseigne = str(df_dirty.loc[i, 'enseigne_concurrent'])
                # Ajouter des variantes
                variants = [current_enseigne.lower(), current_enseigne.upper(), 
                           current_enseigne + ' ', ' ' + current_enseigne]
                df_dirty.loc[i, 'enseigne_concurrent'] = random.choice(variants)
        
        df_dirty['enseigne_concurrent'] = self.introduce_nulls(df_dirty['enseigne_concurrent'], 0.1)
        
        # 3. Zones de chalandise avec unités incohérentes
        for i in range(len(df_dirty)):
            if np.random.random() < 0.1:
                # Parfois en mètres au lieu de km
                df_dirty.loc[i, 'zone_chalandise_km'] = df_dirty.loc[i, 'zone_chalandise_km'] * 1000
        
        return df_dirty
    
    def create_sales_transactions_data(self) -> pd.DataFrame:
        """Crée des données de transactions avec problèmes"""
        print("💳 Génération des données sales - Transactions...")
        
        # Simuler des transactions sur 6 mois
        start_date = datetime(2024, 1, 1)
        
        transactions = []
        transaction_id = 1
        
        # Charger les magasins pour référence
        magasins_path = os.path.join(self.project_root, 'data', 'magasins_performance.csv')
        magasins = pd.read_csv(magasins_path)
        
        for _ in range(5000):  # 5000 transactions
            # Date avec formats variés
            date = start_date + timedelta(days=random.randint(0, 180))
            
            # Magasin (parfois avec erreurs de référence)
            if np.random.random() < 0.95:
                magasin_id = random.choice(magasins['id_magasin'].values)
            else:
                magasin_id = f"MAG_INEXISTANT_{random.randint(1,10):03d}"
            
            # Montant avec problèmes
            montant = round(random.uniform(5, 500), 2)
            if np.random.random() < 0.02:
                montant = -montant  # Montant négatif erroné
            
            # Catégorie produit avec typos
            categories = ['Alimentaire', 'Textile', 'Électronique', 'Maison', 'Beauté']
            categorie = random.choice(categories)
            if np.random.random() < 0.1:
                categorie = self.introduce_typos(pd.Series([categorie]), 0.5).iloc[0]
            
            transaction = {
                'transaction_id': f"TXN_{transaction_id:06d}",
                'date': date.strftime(random.choice(self.formats_date)),
                'magasin_id': magasin_id,
                'montant': montant,
                'categorie': categorie,
                'client_id': f"CLIENT_{random.randint(1, 1000):04d}" if np.random.random() < 0.8 else None
            }
            
            transactions.append(transaction)
            transaction_id += 1
        
        df_transactions = pd.DataFrame(transactions)
        
        # Introduire des nulls
        df_transactions['client_id'] = self.introduce_nulls(df_transactions['client_id'], 0.2)
        df_transactions['categorie'] = self.introduce_nulls(df_transactions['categorie'], 0.05)
        
        # Quelques doublons
        for _ in range(10):
            dup_row = df_transactions.sample(n=1).copy()
            df_transactions = pd.concat([df_transactions, dup_row], ignore_index=True)
        
        return df_transactions
    
    def generate_all_dirty_data(self):
        """Génère tous les fichiers de données sales"""
        print("🏗️ GÉNÉRATION DU DATASET SALE")
        print("=" * 50)
        
        # Créer les répertoires si nécessaire
        os.makedirs(self.raw_data_path, exist_ok=True)
        
        # 1. Magasins sales
        df_magasins_dirty = self.create_dirty_magasins_data()
        magasins_path = os.path.join(self.raw_data_path, 'magasins_raw.csv')
        df_magasins_dirty.to_csv(magasins_path, index=False, encoding='utf-8')
        print(f"✅ Magasins sales: {len(df_magasins_dirty)} lignes -> {magasins_path}")
        
        # 2. Concurrents sales  
        df_competitors_dirty = self.create_dirty_competitors_data()
        competitors_path = os.path.join(self.raw_data_path, 'concurrents_raw.csv')
        df_competitors_dirty.to_csv(competitors_path, index=False, encoding='utf-8')
        print(f"✅ Concurrents sales: {len(df_competitors_dirty)} lignes -> {competitors_path}")
        
        # 3. Transactions sales
        df_transactions_dirty = self.create_sales_transactions_data()
        transactions_path = os.path.join(self.raw_data_path, 'transactions_raw.csv')
        df_transactions_dirty.to_csv(transactions_path, index=False, encoding='utf-8')
        print(f"✅ Transactions sales: {len(df_transactions_dirty)} lignes -> {transactions_path}")
        
        print("\n🎯 RÉSUMÉ DES PROBLÈMES INTRODUITS:")
        print("- Valeurs nulles variées (NULL, '', N/A, etc.)")
        print("- Erreurs de frappe et casse incohérente")
        print("- Formats de dates multiples")
        print("- Doublons partiels")
        print("- Valeurs aberrantes")
        print("- Espaces indésirables")
        print("- Références cassées")
        print("- Unités incohérentes")
        print("\n🚀 Prêt pour le pipeline de nettoyage !")
        
        return {
            'magasins': magasins_path,
            'concurrents': competitors_path,
            'transactions': transactions_path
        }

if __name__ == "__main__":
    generator = DirtyDataGenerator()
    files = generator.generate_all_dirty_data()
    
    print(f"\n📁 Fichiers générés dans: {generator.raw_data_path}")
    for name, path in files.items():
        print(f"  - {name}: {os.path.basename(path)}")