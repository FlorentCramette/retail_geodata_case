#!/usr/bin/env python3
"""
Pipeline quotidien automatisé pour récupération et traitement des données retail
Simule une approche production réelle avec gestion d'erreurs et monitoring
"""

import os
import sys
import logging
import schedule
import time
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import requests
from typing import Dict, List, Optional

# Ajouter le dossier parent au path pour imports
sys.path.append(str(Path(__file__).parent.parent))

from pipeline.preprocessing.data_cleaner import DataCleaner
from pipeline.preprocessing.data_validator import DataValidator

class DailyPipelineOrchestrator:
    """
    Orchestrateur pour pipeline quotidien de données retail
    Simule récupération depuis sources externes + traitement
    """
    
    def __init__(self, config_path: str = "automation/config.json"):
        self.project_root = Path(__file__).parent.parent
        self.config_path = self.project_root / config_path
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configure le logging pour monitoring production"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"daily_pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Charge la configuration (sources de données, credentials, etc.)"""
        # En production, ceci viendrait d'un fichier config sécurisé
        self.config = {
            "data_sources": {
                "ftp_server": "ftp://data.retailcompany.com",
                "api_endpoints": {
                    "magasins": "https://api.pos-system.com/v1/stores",
                    "transactions": "https://api.pos-system.com/v1/transactions",
                    "concurrents": "https://api.market-intel.com/v1/competitors"
                },
                "file_patterns": {
                    "magasins": "magasins_*.csv",
                    "transactions": "transactions_*.csv", 
                    "concurrents": "concurrents_*.csv"
                }
            },
            "retention_days": 30,
            "notification": {
                "slack_webhook": "https://hooks.slack.com/...",
                "email_alerts": ["data-team@company.com"]
            }
        }
        
    def fetch_daily_data(self) -> Dict[str, bool]:
        """
        Récupère les données quotidiennes depuis différentes sources
        Simule FTP, API, SFTP, etc.
        """
        self.logger.info("🔄 Starting daily data fetch...")
        
        results = {}
        today = datetime.now().strftime('%Y%m%d')
        raw_dir = self.project_root / "data" / "raw"
        
        try:
            # Simulation 1: Récupération FTP/SFTP
            results['ftp_fetch'] = self._simulate_ftp_fetch(raw_dir, today)
            
            # Simulation 2: API calls
            results['api_fetch'] = self._simulate_api_fetch(raw_dir, today)
            
            # Simulation 3: Email attachments / SharePoint
            results['email_fetch'] = self._simulate_email_fetch(raw_dir, today)
            
            self.logger.info(f"✅ Data fetch completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Data fetch failed: {str(e)}")
            self._send_alert(f"Data fetch failed: {str(e)}")
            return {}
            
    def _simulate_ftp_fetch(self, raw_dir: Path, date_suffix: str) -> bool:
        """Simule récupération FTP (magasins depuis ERP)"""
        self.logger.info("📁 Fetching from FTP server...")
        
        # En réalité: ftplib, paramiko pour SFTP, ou azure-storage-file
        # from ftplib import FTP
        # ftp = FTP('ftp.company.com')
        # ftp.login(user, password)
        
        # Simulation: copie du fichier généré hier
        source_file = raw_dir / "magasins_dirty.csv"
        target_file = raw_dir / f"magasins_{date_suffix}.csv"
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            self.logger.info(f"📋 Fetched magasins data: {target_file}")
            return True
        return False
        
    def _simulate_api_fetch(self, raw_dir: Path, date_suffix: str) -> bool:
        """Simule récupération API (transactions depuis POS)"""
        self.logger.info("🌐 Fetching from API endpoints...")
        
        # En réalité: requests avec authentification
        # headers = {'Authorization': f'Bearer {api_token}'}
        # response = requests.get(api_url, headers=headers, params=params)
        
        # Simulation: copie des transactions
        source_file = raw_dir / "transactions_dirty.csv" 
        target_file = raw_dir / f"transactions_{date_suffix}.csv"
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            self.logger.info(f"💳 Fetched transactions data: {target_file}")
            return True
        return False
        
    def _simulate_email_fetch(self, raw_dir: Path, date_suffix: str) -> bool:
        """Simule récupération email (concurrents depuis veille marché)"""
        self.logger.info("📧 Fetching from email attachments...")
        
        # En réalité: imaplib, exchangelib, ou O365 API
        # import imaplib
        # mail = imaplib.IMAP4_SSL('outlook.office365.com')
        # mail.login(email, password)
        
        # Simulation: copie des données concurrents
        source_file = raw_dir / "concurrents_dirty.csv"
        target_file = raw_dir / f"concurrents_{date_suffix}.csv"
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            self.logger.info(f"🏢 Fetched competitors data: {target_file}")
            return True
        return False
        
    def run_data_pipeline(self, date_suffix: str) -> bool:
        """Execute le pipeline de nettoyage sur les données du jour"""
        self.logger.info("🧹 Running data cleaning pipeline...")
        
        try:
            # Utilise notre pipeline existant
            from pipeline.main_pipeline import DataPipelineOrchestrator
            
            orchestrator = DataPipelineOrchestrator()
            result = orchestrator.run_full_pipeline()
            
            if result.get('success', False):
                self.logger.info("✅ Data pipeline completed successfully")
                return True
            else:
                self.logger.error("❌ Data pipeline failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Pipeline execution failed: {str(e)}")
            self._send_alert(f"Pipeline failed: {str(e)}")
            return False
            
    def cleanup_old_data(self):
        """Nettoie les anciennes données selon la politique de rétention"""
        self.logger.info("🧽 Cleaning up old data...")
        
        cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
        
        for data_dir in ['raw', 'staging', 'processed']:
            dir_path = self.project_root / "data" / data_dir
            if not dir_path.exists():
                continue
                
            for file_path in dir_path.glob("*_202*.csv"):
                try:
                    # Extract date from filename
                    date_str = file_path.stem.split('_')[-1]
                    if len(date_str) == 8:  # YYYYMMDD format
                        file_date = datetime.strptime(date_str, '%Y%m%d')
                        if file_date < cutoff_date:
                            file_path.unlink()
                            self.logger.info(f"🗑️ Deleted old file: {file_path}")
                except (ValueError, IndexError):
                    continue
                    
    def _send_alert(self, message: str):
        """Envoie des alertes en cas d'erreur"""
        self.logger.info(f"🚨 Sending alert: {message}")
        
        # En production: Slack, Teams, email, PagerDuty
        # import requests
        # requests.post(self.config['notification']['slack_webhook'], 
        #               json={'text': f'🚨 Pipeline Alert: {message}'})
        
    def generate_daily_report(self):
        """Génère un rapport quotidien de santé du pipeline"""
        self.logger.info("📊 Generating daily report...")
        
        report_dir = self.project_root / "reports" / "daily"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().strftime('%Y%m%d')
        report_file = report_dir / f"daily_report_{today}.md"
        
        # Collecte des métriques
        processed_dir = self.project_root / "data" / "processed"
        metrics = {}
        
        for file_name in ["magasins_performance.csv", "transactions.csv"]:
            file_path = processed_dir / file_name
            if file_path.exists():
                df = pd.read_csv(file_path)
                metrics[file_name] = {
                    'records': len(df),
                    'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                }
                
        # Génère le rapport
        report_content = f"""# Daily Pipeline Report - {today}

## 📊 Data Processing Summary
- **Execution Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: ✅ SUCCESS

## 📈 Data Metrics
"""
        
        for file_name, data in metrics.items():
            report_content += f"""
### {file_name}
- Records: {data['records']:,}
- Last Updated: {data['last_modified'].strftime('%Y-%m-%d %H:%M:%S')}
"""
            
        report_content += f"""
## 🎯 Next Steps
- Monitor data quality trends
- Review pipeline performance
- Check for data anomalies

Generated by: Daily Pipeline Orchestrator
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        self.logger.info(f"📋 Daily report saved: {report_file}")
        
    def run_daily_job(self):
        """Job principal exécuté chaque jour"""
        self.logger.info("🚀 Starting daily pipeline job...")
        
        start_time = datetime.now()
        today = start_time.strftime('%Y%m%d')
        
        try:
            # 1. Récupération des données
            fetch_results = self.fetch_daily_data()
            
            # 2. Exécution du pipeline si données disponibles
            if any(fetch_results.values()):
                pipeline_success = self.run_data_pipeline(today)
                
                if pipeline_success:
                    # 3. Nettoyage des anciennes données
                    self.cleanup_old_data()
                    
                    # 4. Génération du rapport
                    self.generate_daily_report()
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    self.logger.info(f"✅ Daily job completed in {execution_time:.1f} seconds")
                else:
                    self.logger.error("❌ Daily job failed during pipeline execution")
            else:
                self.logger.warning("⚠️ No new data fetched, skipping pipeline")
                
        except Exception as e:
            self.logger.error(f"❌ Daily job failed: {str(e)}")
            self._send_alert(f"Daily job failed: {str(e)}")

def setup_scheduler():
    """Configure le scheduler pour exécution automatique"""
    orchestrator = DailyPipelineOrchestrator()
    
    # Planification quotidienne à 6h du matin
    schedule.every().day.at("06:00").do(orchestrator.run_daily_job)
    
    # Planification pour test (toutes les 5 minutes)
    # schedule.every(5).minutes.do(orchestrator.run_daily_job)
    
    print("📅 Scheduler configured:")
    print("- Daily execution at 06:00 AM")
    print("- Logs saved to logs/ directory")
    print("- Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n👋 Scheduler stopped")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Retail Data Pipeline")
    parser.add_argument("--mode", choices=["run-once", "scheduler"], 
                       default="run-once", help="Execution mode")
    parser.add_argument("--test", action="store_true", 
                       help="Run in test mode with current data")
    
    args = parser.parse_args()
    
    if args.mode == "scheduler":
        setup_scheduler()
    else:
        # Exécution unique
        orchestrator = DailyPipelineOrchestrator()
        orchestrator.run_daily_job()