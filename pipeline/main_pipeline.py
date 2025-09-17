"""
Pipeline principal d'orchestration des données
Coordonne le nettoyage, la validation et la mise à disposition des données pour ML/Dashboard
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any
import pandas as pd

# Ajouter le répertoire pipeline au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, 'pipeline'))

# Imports des modules du pipeline
from preprocessing.data_cleaner import DataCleaner
from preprocessing.data_validator import DataValidator

class DataPipelineOrchestrator:
    """Orchestrateur principal du pipeline de données"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or self._get_project_root()
        self.raw_path = os.path.join(self.project_root, 'data', 'raw')
        self.staging_path = os.path.join(self.project_root, 'data', 'staging')
        self.processed_path = os.path.join(self.project_root, 'data', 'processed')
        
        # Configuration du logging
        self.setup_logging()
        
        # Statistiques du pipeline
        self.pipeline_stats = {}
    
    def _get_project_root(self) -> str:
        """Trouve la racine du projet"""
        return os.path.dirname(current_dir)
    
    def setup_logging(self):
        """Configure le logging principal"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format)
        self.logger = logging.getLogger('PipelineOrchestrator')
        
        # Créer un fichier de log pour le pipeline complet
        log_dir = os.path.join(self.project_root, 'pipeline', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f'pipeline_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        self.logger.addHandler(file_handler)
    
    def check_raw_data_availability(self) -> bool:
        """Vérifie que les données brutes sont disponibles"""
        required_files = [
            'magasins_raw.csv',
            'concurrents_raw.csv', 
            'transactions_raw.csv'
        ]
        
        missing_files = []
        for file in required_files:
            file_path = os.path.join(self.raw_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            self.logger.error(f"Missing raw data files: {missing_files}")
            return False
        
        self.logger.info("All raw data files available")
        return True
    
    def run_data_cleaning(self) -> Dict[str, Any]:
        """Exécute l'étape de nettoyage des données"""
        self.logger.info("=== STEP 1: DATA CLEANING ===")
        
        try:
            cleaner = DataCleaner(self.project_root)
            cleaned_data = cleaner.run_full_pipeline()
            
            # Récupérer les statistiques de nettoyage
            self.pipeline_stats['cleaning'] = cleaner.cleaning_stats
            
            self.logger.info("Data cleaning completed successfully")
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"Data cleaning failed: {e}")
            raise
    
    def run_data_validation(self) -> Dict[str, Any]:
        """Exécute la validation des données nettoyées"""
        self.logger.info("=== STEP 2: DATA VALIDATION ===")
        
        try:
            validator = DataValidator(self.project_root)
            validation_results = validator.run_validation_pipeline()
            
            # Stocker les résultats de validation
            self.pipeline_stats['validation'] = validation_results.get('summary', {})
            
            # Vérifier si la validation a réussi
            if not validation_results.get('summary', {}).get('overall_success', False):
                self.logger.warning("Some data validation tests failed!")
                
                # Décider si continuer ou arrêter
                failed_rate = 100 - validation_results.get('summary', {}).get('overall_success_rate', 0)
                if failed_rate > 20:  # Si plus de 20% d'échec, arrêter
                    raise ValueError(f"Too many validation failures ({failed_rate:.1f}%)")
            
            self.logger.info("Data validation completed successfully")
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Data validation failed: {e}")
            raise
    
    def prepare_processed_data(self):
        """Prépare les données finales pour ML et Dashboard"""
        self.logger.info("=== STEP 3: PREPARE PROCESSED DATA ===")
        
        try:
            # Créer le répertoire processed
            os.makedirs(self.processed_path, exist_ok=True)
            
            # Copier les données validées vers processed
            staging_files = {
                'magasins_staging.csv': 'magasins_performance.csv',
                'concurrents_staging.csv': 'sites_concurrents.csv', 
                'transactions_staging.csv': 'transactions.csv'
            }
            
            for staging_file, processed_file in staging_files.items():
                staging_path = os.path.join(self.staging_path, staging_file)
                processed_path = os.path.join(self.processed_path, processed_file)
                
                if os.path.exists(staging_path):
                    df = pd.read_csv(staging_path)
                    df.to_csv(processed_path, index=False)
                    self.logger.info(f"Prepared {processed_file}: {len(df)} records")
            
            # Créer un fichier de métadonnées
            metadata = {
                'pipeline_run_time': datetime.now().isoformat(),
                'data_freshness': datetime.now().isoformat(),
                'pipeline_version': '1.0.0',
                'processing_stats': self.pipeline_stats
            }
            
            import json
            metadata_path = os.path.join(self.processed_path, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            self.logger.info("Processed data preparation completed")
            
        except Exception as e:
            self.logger.error(f"Processed data preparation failed: {e}")
            raise
    
    def update_ml_and_dashboard_data(self):
        """Met à jour les données pour les modèles ML et le dashboard"""
        self.logger.info("=== STEP 4: UPDATE ML/DASHBOARD DATA ===")
        
        try:
            # Mise à jour des données pour les modèles ML et dashboard
            main_data_path = os.path.join(self.project_root, 'data')
            
            # Copier les principales données
            processed_files = {
                'magasins_performance.csv': 'magasins_performance.csv',
                'sites_concurrents.csv': 'sites_concurrents.csv'
            }
            
            for processed_file, main_file in processed_files.items():
                processed_path = os.path.join(self.processed_path, processed_file)
                main_path = os.path.join(main_data_path, main_file)
                
                if os.path.exists(processed_path):
                    df = pd.read_csv(processed_path)
                    
                    # Créer une sauvegarde de l'ancien fichier
                    if os.path.exists(main_path):
                        backup_path = main_path.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
                        os.rename(main_path, backup_path)
                        self.logger.info(f"Backed up {main_file}")
                    
                    # Copier les nouvelles données
                    df.to_csv(main_path, index=False)
                    self.logger.info(f"Updated {main_file} with {len(df)} records")
            
            self.logger.info("ML/Dashboard data update completed")
            
        except Exception as e:
            self.logger.error(f"ML/Dashboard data update failed: {e}")
            raise
    
    def generate_pipeline_report(self) -> str:
        """Génère un rapport complet du pipeline"""
        report = []
        report.append("🚀 DATA PIPELINE EXECUTION REPORT")
        report.append("=" * 60)
        report.append(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Project Root: {self.project_root}")
        report.append("")
        
        # Statistiques de nettoyage
        if 'cleaning' in self.pipeline_stats:
            report.append("🧹 DATA CLEANING RESULTS:")
            for dataset, stats in self.pipeline_stats['cleaning'].items():
                if stats:
                    report.append(f"  {dataset}: {stats['initial_count']} → {stats['final_count']} records ({stats['cleaning_rate']:.1f}% cleaned)")
            report.append("")
        
        # Statistiques de validation
        if 'validation' in self.pipeline_stats:
            validation = self.pipeline_stats['validation']
            status = "✅ PASSED" if validation.get('overall_success', False) else "❌ FAILED"
            report.append(f"🔍 DATA VALIDATION: {status}")
            report.append(f"  Success Rate: {validation.get('overall_success_rate', 0):.1f}%")
            report.append(f"  Tests: {validation.get('passed_tests', 0)}/{validation.get('total_tests', 0)}")
            report.append("")
        
        # Files créés
        report.append("📁 FILES CREATED:")
        if os.path.exists(self.processed_path):
            for file in os.listdir(self.processed_path):
                file_path = os.path.join(self.processed_path, file)
                if os.path.isfile(file_path):
                    report.append(f"  {file}")
        report.append("")
        
        report.append("🎯 PIPELINE STATUS: COMPLETED SUCCESSFULLY")
        report.append("")
        report.append("Next steps:")
        report.append("- Run ML models with updated data")
        report.append("- Launch dashboard to view results")
        report.append("- Set up automated scheduling if needed")
        
        report_text = "\n".join(report)
        
        # Sauvegarder le rapport
        reports_dir = os.path.join(self.project_root, 'pipeline', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        report_path = os.path.join(reports_dir, 
                                  f'pipeline_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        self.logger.info(f"Pipeline report saved to {report_path}")
        
        return report_text
    
    def run_full_pipeline(self, skip_validation: bool = False):
        """Exécute le pipeline complet de données"""
        self.logger.info("🚀 Starting full data pipeline execution...")
        
        start_time = datetime.now()
        
        try:
            # 1. Vérifier les données brutes
            if not self.check_raw_data_availability():
                self.logger.info("Generating dirty data first...")
                
                # Importer et exécuter le générateur de données sales
                sys.path.append(os.path.join(self.project_root, 'scripts'))
                from generate_dirty_data import DirtyDataGenerator
                
                generator = DirtyDataGenerator()
                generator.generate_all_dirty_data()
                
                if not self.check_raw_data_availability():
                    raise FileNotFoundError("Could not generate or find raw data files")
            
            # 2. Nettoyage des données
            cleaned_data = self.run_data_cleaning()
            
            # 3. Validation des données (optionnel)
            if not skip_validation:
                validation_results = self.run_data_validation()
            else:
                self.logger.info("Skipping data validation")
            
            # 4. Préparation des données finales
            self.prepare_processed_data()
            
            # 5. Mise à jour des données ML/Dashboard
            self.update_ml_and_dashboard_data()
            
            # 6. Génération du rapport
            execution_time = (datetime.now() - start_time).total_seconds()
            self.pipeline_stats['execution_time_seconds'] = execution_time
            
            report = self.generate_pipeline_report()
            print(report)
            
            self.logger.info(f"✅ Full pipeline completed successfully in {execution_time:.1f} seconds")
            
            return {
                'success': True,
                'execution_time': execution_time,
                'stats': self.pipeline_stats,
                'cleaned_data': cleaned_data if 'cleaned_data' in locals() else None
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ Pipeline failed after {execution_time:.1f} seconds: {e}")
            
            return {
                'success': False,
                'execution_time': execution_time,
                'error': str(e),
                'stats': self.pipeline_stats
            }

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Pipeline Orchestrator')
    parser.add_argument('--skip-validation', action='store_true', 
                       help='Skip data validation step')
    parser.add_argument('--project-root', type=str, 
                       help='Project root directory')
    
    args = parser.parse_args()
    
    # Exécuter le pipeline
    orchestrator = DataPipelineOrchestrator(args.project_root)
    result = orchestrator.run_full_pipeline(skip_validation=args.skip_validation)
    
    # Code de sortie basé sur le succès
    exit_code = 0 if result['success'] else 1
    exit(exit_code)

if __name__ == "__main__":
    main()