"""
Pipeline de prétraitement de données avec validation et nettoyage
Traite les données 'sales' pour les transformer en données propres utilisables
"""

import pandas as pd
import numpy as np
import re
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import warnings

class DataCleaner:
    """Nettoyeur de données avec validation et transformations"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or self._get_project_root()
        self.raw_path = os.path.join(self.project_root, 'data', 'raw')
        self.staging_path = os.path.join(self.project_root, 'data', 'staging')
        self.processed_path = os.path.join(self.project_root, 'data', 'processed')
        
        # Configuration du logging
        self.setup_logging()
        
        # Statistiques de nettoyage
        self.cleaning_stats = {
            'magasins': {},
            'concurrents': {},
            'transactions': {}
        }
        
    def _get_project_root(self) -> str:
        """Trouve la racine du projet"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(current_dir))
    
    def setup_logging(self):
        """Configure le logging pour le pipeline"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format)
        self.logger = logging.getLogger('DataCleaner')
        
        # Créer aussi un fichier de log
        log_dir = os.path.join(self.project_root, 'pipeline', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f'data_cleaning_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        self.logger.addHandler(file_handler)
    
    def clean_null_values(self, df: pd.DataFrame, column: str, strategy: str = 'remove') -> pd.DataFrame:
        """Nettoie les valeurs nulles d'une colonne"""
        # Identifier les valeurs nulles multiples
        null_variants = ['', '  ', 'NULL', 'null', 'N/A', 'n/a', '#N/A', 'None', None, np.nan]
        
        # Compter les nulls avant nettoyage
        null_count_before = df[column].isin(null_variants).sum() + df[column].isna().sum()
        
        # Remplacer les variantes de null par np.nan
        df[column] = df[column].replace(null_variants, np.nan)
        
        if strategy == 'remove':
            df = df.dropna(subset=[column])
        elif strategy == 'forward_fill':
            df[column] = df[column].fillna(method='ffill')
        elif strategy == 'backward_fill':
            df[column] = df[column].fillna(method='bfill')
        elif strategy == 'median' and df[column].dtype in ['int64', 'float64']:
            df[column] = df[column].fillna(df[column].median())
        elif strategy == 'mode':
            mode_value = df[column].mode()
            if len(mode_value) > 0:
                df[column] = df[column].fillna(mode_value.iloc[0])
        
        null_count_after = df[column].isna().sum()
        
        self.logger.info(f"Column {column}: {null_count_before} nulls -> {null_count_after} nulls (strategy: {strategy})")
        
        return df
    
    def clean_text_column(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Nettoie une colonne texte (espaces, casse, caractères spéciaux)"""
        if column not in df.columns:
            return df
            
        original_values = df[column].dropna().unique()
        
        # Nettoyer les espaces
        df[column] = df[column].astype(str).str.strip()
        
        # Standardiser la casse (première lettre majuscule)
        df[column] = df[column].str.title()
        
        # Corriger les doublons d'espaces
        df[column] = df[column].str.replace(r'\s+', ' ', regex=True)
        
        # Replacer les valeurs vides par nan
        df[column] = df[column].replace(['', 'Nan'], np.nan)
        
        cleaned_values = df[column].dropna().unique()
        
        self.logger.info(f"Column {column}: {len(original_values)} -> {len(cleaned_values)} unique values")
        
        return df
    
    def clean_coordinate_format(self, df: pd.DataFrame, lat_col: str, lon_col: str) -> pd.DataFrame:
        """Nettoie et standardise les coordonnées géographiques"""
        
        def fix_coordinate(value):
            """Convertit les coordonnées au bon format"""
            if pd.isna(value):
                return np.nan
                
            # Convertir en string puis remplacer virgules par points
            str_val = str(value).replace(',', '.')
            
            try:
                float_val = float(str_val)
                return float_val
            except:
                return np.nan
        
        # Nettoyer latitude
        if lat_col in df.columns:
            df[lat_col] = df[lat_col].apply(fix_coordinate)
            
            # Valider les plages de latitude (France: 41-51°N)
            invalid_lat = (df[lat_col] < 41) | (df[lat_col] > 51)
            invalid_lat_count = invalid_lat.sum()
            
            if invalid_lat_count > 0:
                self.logger.warning(f"Found {invalid_lat_count} invalid latitude values")
                df.loc[invalid_lat, lat_col] = np.nan
        
        # Nettoyer longitude
        if lon_col in df.columns:
            df[lon_col] = df[lon_col].apply(fix_coordinate)
            
            # Valider les plages de longitude (France: -5 à 10°E)
            invalid_lon = (df[lon_col] < -5) | (df[lon_col] > 10)
            invalid_lon_count = invalid_lon.sum()
            
            if invalid_lon_count > 0:
                self.logger.warning(f"Found {invalid_lon_count} invalid longitude values")
                df.loc[invalid_lon, lon_col] = np.nan
        
        return df
    
    def clean_date_formats(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """Standardise les formats de dates multiples"""
        if date_col not in df.columns:
            return df
        
        # Formats de date à essayer
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']
        
        def parse_date(date_str):
            """Essaie de parser une date avec différents formats"""
            if pd.isna(date_str) or str(date_str).strip() == '':
                return np.nan
                
            date_str = str(date_str).strip()
            
            # Dates invalides évidentes
            invalid_patterns = ['32/', '13/', '00/00/', '/2023', '31/02/', '30/02/']
            if any(pattern in date_str for pattern in invalid_patterns):
                return np.nan
            
            for fmt in date_formats:
                try:
                    return pd.to_datetime(date_str, format=fmt)
                except:
                    continue
            
            # Essayer le parser automatique en dernier recours
            try:
                return pd.to_datetime(date_str, dayfirst=True)
            except:
                return np.nan
        
        original_count = len(df[date_col].dropna())
        df[date_col] = df[date_col].apply(parse_date)
        parsed_count = len(df[date_col].dropna())
        
        self.logger.info(f"Date column {date_col}: {original_count} -> {parsed_count} valid dates")
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame, subset_cols: List[str] = None) -> pd.DataFrame:
        """Supprime les doublons basés sur des colonnes spécifiques"""
        initial_count = len(df)
        
        if subset_cols:
            df = df.drop_duplicates(subset=subset_cols, keep='first')
        else:
            df = df.drop_duplicates(keep='first')
        
        final_count = len(df)
        removed_count = initial_count - final_count
        
        self.logger.info(f"Duplicates removed: {removed_count} ({removed_count/initial_count*100:.1f}%)")
        
        return df
    
    def detect_outliers(self, df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.Series:
        """Détecte les valeurs aberrantes dans une colonne numérique"""
        if column not in df.columns or df[column].dtype not in ['int64', 'float64']:
            return pd.Series([False] * len(df), index=df.index)
        
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
            
        elif method == 'zscore':
            z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
            outliers = z_scores > 3
        
        outlier_count = outliers.sum()
        self.logger.info(f"Outliers detected in {column}: {outlier_count} ({outlier_count/len(df)*100:.1f}%)")
        
        return outliers
    
    def clean_magasins_data(self) -> pd.DataFrame:
        """Nettoie les données des magasins"""
        self.logger.info("🏪 Starting magasins data cleaning...")
        
        # Charger les données sales
        raw_file = os.path.join(self.raw_path, 'magasins_raw.csv')
        df = pd.read_csv(raw_file)
        
        initial_count = len(df)
        self.logger.info(f"Loaded {initial_count} raw magasin records")
        
        # 1. Nettoyer les villes
        df = self.clean_text_column(df, 'ville')
        df = self.clean_null_values(df, 'ville', 'remove')
        
        # 2. Nettoyer les coordonnées
        df = self.clean_coordinate_format(df, 'latitude', 'longitude')
        df = self.clean_null_values(df, 'latitude', 'remove')
        df = self.clean_null_values(df, 'longitude', 'remove')
        
        # 3. Nettoyer les dates
        if 'date_ouverture' in df.columns:
            df = self.clean_date_formats(df, 'date_ouverture')
        
        # 4. Nettoyer les valeurs numériques
        numeric_cols = ['ca_annuel', 'population_zone_1km', 'surface_vente', 'effectif']
        for col in numeric_cols:
            if col in df.columns:
                # Détecter et supprimer les valeurs aberrantes
                outliers = self.detect_outliers(df, col)
                df.loc[outliers, col] = np.nan
                
                # Imputer les valeurs manquantes par la médiane
                df = self.clean_null_values(df, col, 'median')
        
        # 5. Supprimer les doublons basés sur les coordonnées
        df = self.remove_duplicates(df, ['latitude', 'longitude'])
        
        # 6. Nettoyer les IDs doublons
        df = df[~df['id_magasin'].str.contains('DUP', na=False)]
        
        final_count = len(df)
        self.cleaning_stats['magasins'] = {
            'initial_count': initial_count,
            'final_count': final_count,
            'removed_count': initial_count - final_count,
            'cleaning_rate': (initial_count - final_count) / initial_count * 100
        }
        
        self.logger.info(f"✅ Magasins cleaned: {initial_count} -> {final_count} records")
        
        return df
    
    def clean_concurrents_data(self) -> pd.DataFrame:
        """Nettoie les données des concurrents"""
        self.logger.info("🏢 Starting concurrents data cleaning...")
        
        # Charger les données sales
        raw_file = os.path.join(self.raw_path, 'concurrents_raw.csv')
        df = pd.read_csv(raw_file)
        
        initial_count = len(df)
        
        # 1. Nettoyer les coordonnées
        df = self.clean_coordinate_format(df, 'latitude', 'longitude')
        df = self.clean_null_values(df, 'latitude', 'remove')
        df = self.clean_null_values(df, 'longitude', 'remove')
        
        # 2. Nettoyer les types et enseignes
        df = self.clean_text_column(df, 'type_concurrent')
        df = self.clean_text_column(df, 'enseigne_concurrent')
        df = self.clean_text_column(df, 'ville_proche')
        
        # 3. Corriger les unités incohérentes pour zone_chalandise_km
        if 'zone_chalandise_km' in df.columns:
            # Si la valeur est > 100, c'est probablement en mètres
            mask_meters = df['zone_chalandise_km'] > 100
            df.loc[mask_meters, 'zone_chalandise_km'] = df.loc[mask_meters, 'zone_chalandise_km'] / 1000
            
            self.logger.info(f"Converted {mask_meters.sum()} zone values from meters to km")
        
        # 4. Nettoyer les valeurs numériques
        numeric_cols = ['surface_prevue', 'investissement', 'zone_chalandise_km']
        for col in numeric_cols:
            if col in df.columns:
                df = self.clean_null_values(df, col, 'median')
        
        # 5. Supprimer les doublons
        df = self.remove_duplicates(df, ['latitude', 'longitude'])
        
        final_count = len(df)
        self.cleaning_stats['concurrents'] = {
            'initial_count': initial_count,
            'final_count': final_count,
            'removed_count': initial_count - final_count,
            'cleaning_rate': (initial_count - final_count) / initial_count * 100
        }
        
        self.logger.info(f"✅ Concurrents cleaned: {initial_count} -> {final_count} records")
        
        return df
    
    def clean_transactions_data(self) -> pd.DataFrame:
        """Nettoie les données des transactions"""
        self.logger.info("💳 Starting transactions data cleaning...")
        
        # Charger les données sales
        raw_file = os.path.join(self.raw_path, 'transactions_raw.csv')
        df = pd.read_csv(raw_file)
        
        initial_count = len(df)
        
        # 1. Nettoyer les dates
        df = self.clean_date_formats(df, 'date')
        df = self.clean_null_values(df, 'date', 'remove')
        
        # 2. Nettoyer les montants
        # Supprimer les montants négatifs (erreurs)
        if 'montant' in df.columns:
            negative_count = (df['montant'] < 0).sum()
            if negative_count > 0:
                self.logger.warning(f"Removing {negative_count} negative transaction amounts")
                df = df[df['montant'] >= 0]
            
            # Détecter et traiter les outliers
            outliers = self.detect_outliers(df, 'montant')
            outlier_threshold = df['montant'].quantile(0.99)  # Cap à 99e percentile
            df.loc[outliers, 'montant'] = np.minimum(df.loc[outliers, 'montant'], outlier_threshold)
        
        # 3. Nettoyer les catégories
        df = self.clean_text_column(df, 'categorie')
        df = self.clean_null_values(df, 'categorie', 'mode')
        
        # 4. Valider les références magasin
        if 'magasin_id' in df.columns:
            # Supprimer les références inexistantes
            invalid_refs = df['magasin_id'].str.contains('INEXISTANT', na=False)
            invalid_count = invalid_refs.sum()
            if invalid_count > 0:
                self.logger.warning(f"Removing {invalid_count} transactions with invalid magasin_id")
                df = df[~invalid_refs]
        
        # 5. Supprimer les doublons complets
        df = self.remove_duplicates(df)
        
        final_count = len(df)
        self.cleaning_stats['transactions'] = {
            'initial_count': initial_count,
            'final_count': final_count,
            'removed_count': initial_count - final_count,
            'cleaning_rate': (initial_count - final_count) / initial_count * 100
        }
        
        self.logger.info(f"✅ Transactions cleaned: {initial_count} -> {final_count} records")
        
        return df
    
    def save_staging_data(self, df: pd.DataFrame, filename: str):
        """Sauvegarde les données nettoyées en staging"""
        output_path = os.path.join(self.staging_path, filename)
        df.to_csv(output_path, index=False)
        self.logger.info(f"💾 Saved {len(df)} records to {output_path}")
    
    def generate_cleaning_report(self) -> str:
        """Génère un rapport de nettoyage"""
        report = []
        report.append("📊 DATA CLEANING REPORT")
        report.append("=" * 50)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for dataset, stats in self.cleaning_stats.items():
            if stats:
                report.append(f"🔧 {dataset.upper()}")
                report.append(f"  Initial records: {stats['initial_count']:,}")
                report.append(f"  Final records: {stats['final_count']:,}")
                report.append(f"  Removed: {stats['removed_count']:,}")
                report.append(f"  Cleaning rate: {stats['cleaning_rate']:.1f}%")
                report.append("")
        
        report_text = "\n".join(report)
        
        # Sauvegarder le rapport
        report_path = os.path.join(self.project_root, 'pipeline', 'logs', 
                                  f'cleaning_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return report_text
    
    def run_full_pipeline(self):
        """Exécute le pipeline complet de nettoyage"""
        self.logger.info("🚀 Starting full data cleaning pipeline...")
        
        # Créer les répertoires si nécessaire
        os.makedirs(self.staging_path, exist_ok=True)
        os.makedirs(os.path.join(self.project_root, 'pipeline', 'logs'), exist_ok=True)
        
        try:
            # 1. Nettoyer les magasins
            magasins_clean = self.clean_magasins_data()
            self.save_staging_data(magasins_clean, 'magasins_staging.csv')
            
            # 2. Nettoyer les concurrents
            concurrents_clean = self.clean_concurrents_data()
            self.save_staging_data(concurrents_clean, 'concurrents_staging.csv')
            
            # 3. Nettoyer les transactions
            transactions_clean = self.clean_transactions_data()
            self.save_staging_data(transactions_clean, 'transactions_staging.csv')
            
            # 4. Générer le rapport
            report = self.generate_cleaning_report()
            print(report)
            
            self.logger.info("✅ Full pipeline completed successfully!")
            
            return {
                'magasins': magasins_clean,
                'concurrents': concurrents_clean,
                'transactions': transactions_clean
            }
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {str(e)}")
            raise

if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaned_data = cleaner.run_full_pipeline()