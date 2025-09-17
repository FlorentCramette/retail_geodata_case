"""
DAG Airflow pour pipeline quotidien retail
Exemple d'implémentation avec Apache Airflow
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 9, 17),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['data-team@company.com']
}

dag = DAG(
    'retail_daily_pipeline',
    default_args=default_args,
    description='Pipeline quotidien données retail avec nettoyage et validation',
    schedule_interval='0 6 * * *',  # 6h du matin tous les jours
    max_active_runs=1,
    catchup=False,
    tags=['retail', 'data-pipeline', 'daily']
)

# Tâche 1: Vérifier disponibilité des sources de données
check_ftp_availability = HttpSensor(
    task_id='check_ftp_availability',
    http_conn_id='ftp_server',
    endpoint='health',
    timeout=60,
    poke_interval=30,
    dag=dag
)

# Tâche 2: Récupération données magasins (FTP)
fetch_magasins_data = BashOperator(
    task_id='fetch_magasins_data',
    bash_command="""
    cd /opt/airflow/data && 
    python /opt/airflow/dags/scripts/fetch_ftp_data.py --source magasins --date {{ ds }}
    """,
    dag=dag
)

# Tâche 3: Récupération données transactions (API)
def fetch_transactions_api(**context):
    import requests
    import pandas as pd
    from datetime import datetime
    
    # Configuration API
    api_endpoint = "https://api.pos-system.com/v1/transactions"
    headers = {'Authorization': 'Bearer {{ var.value.api_token }}'}
    
    # Paramètres pour récupérer les données d'hier
    yesterday = context['yesterday_ds']
    params = {
        'date_from': yesterday,
        'date_to': yesterday,
        'format': 'json'
    }
    
    response = requests.get(api_endpoint, headers=headers, params=params)
    response.raise_for_status()
    
    # Sauvegarder en CSV
    data = response.json()
    df = pd.DataFrame(data['transactions'])
    output_path = f"/opt/airflow/data/raw/transactions_{yesterday.replace('-', '')}.csv"
    df.to_csv(output_path, index=False)
    
    return f"Fetched {len(df)} transactions"

fetch_transactions_task = PythonOperator(
    task_id='fetch_transactions_data',
    python_callable=fetch_transactions_api,
    dag=dag
)

# Tâche 4: Attendre que tous les fichiers soient disponibles
wait_for_files = FileSensor(
    task_id='wait_for_all_files',
    filepath='/opt/airflow/data/raw/transactions_{{ ds_nodash }}.csv',
    fs_conn_id='fs_default',
    poke_interval=60,
    timeout=3600,  # 1 heure max
    dag=dag
)

# Tâche 5: Exécuter le pipeline de nettoyage
run_data_cleaning = BashOperator(
    task_id='run_data_cleaning',
    bash_command="""
    cd /opt/airflow && 
    python pipeline/main_pipeline.py --input-date {{ ds }}
    """,
    dag=dag
)

# Tâche 6: Validation des données nettoyées
def validate_cleaned_data(**context):
    from pipeline.preprocessing.data_validator import DataValidator
    
    validator = DataValidator()
    results = validator.run_validation_pipeline()
    
    if results['overall_success_rate'] < 0.95:  # 95% minimum
        raise ValueError(f"Data quality too low: {results['overall_success_rate']:.1%}")
    
    return f"Validation passed: {results['overall_success_rate']:.1%}"

validate_data_task = PythonOperator(
    task_id='validate_cleaned_data',
    python_callable=validate_cleaned_data,
    dag=dag
)

# Tâche 7: Mise à jour des données pour ML/Dashboard
update_production_data = BashOperator(
    task_id='update_production_data',
    bash_command="""
    # Backup des données actuelles
    cp /opt/airflow/data/magasins_performance.csv /opt/airflow/data/backups/magasins_{{ ds }}.csv
    
    # Mise à jour avec nouvelles données
    cp /opt/airflow/data/processed/magasins_performance.csv /opt/airflow/data/magasins_performance.csv
    cp /opt/airflow/data/processed/transactions.csv /opt/airflow/data/transactions.csv
    
    # Redémarrer dashboard si nécessaire
    curl -X POST http://dashboard:8501/refresh-data
    """,
    dag=dag
)

# Tâche 8: Nettoyage des anciennes données
cleanup_old_data = BashOperator(
    task_id='cleanup_old_data',
    bash_command="""
    # Supprimer fichiers de plus de 30 jours
    find /opt/airflow/data/raw -name "*.csv" -mtime +30 -delete
    find /opt/airflow/data/staging -name "*.csv" -mtime +30 -delete
    find /opt/airflow/logs -name "*.log" -mtime +7 -delete
    """,
    dag=dag
)

# Tâche 9: Génération du rapport quotidien
def generate_daily_report(**context):
    import pandas as pd
    from datetime import datetime
    
    # Charger les métriques du pipeline
    report_data = {
        'date': context['ds'],
        'execution_time': datetime.now(),
        'status': 'SUCCESS'
    }
    
    # Ajouter métriques de données
    for dataset in ['magasins_performance', 'transactions']:
        file_path = f"/opt/airflow/data/{dataset}.csv"
        df = pd.read_csv(file_path)
        report_data[f'{dataset}_records'] = len(df)
    
    # Sauvegarder rapport
    report_path = f"/opt/airflow/reports/daily_report_{context['ds']}.json"
    import json
    with open(report_path, 'w') as f:
        json.dump(report_data, f, default=str, indent=2)
    
    # Envoyer notification Slack
    import requests
    slack_webhook = "{{ var.value.slack_webhook }}"
    message = f"📊 Pipeline quotidien terminé avec succès\n" \
             f"Date: {context['ds']}\n" \
             f"Magasins: {report_data.get('magasins_performance_records', 0)} records\n" \
             f"Transactions: {report_data.get('transactions_records', 0)} records"
    
    requests.post(slack_webhook, json={'text': message})

generate_report_task = PythonOperator(
    task_id='generate_daily_report',
    python_callable=generate_daily_report,
    dag=dag
)

# Définition des dépendances
check_ftp_availability >> [fetch_magasins_data, fetch_transactions_task]
[fetch_magasins_data, fetch_transactions_task] >> wait_for_files
wait_for_files >> run_data_cleaning
run_data_cleaning >> validate_data_task
validate_data_task >> update_production_data
update_production_data >> [cleanup_old_data, generate_report_task]