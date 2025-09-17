"""
Validateur de données avec Great Expectations
Définit des tests de qualité automatisés pour surveiller l'intégrité des données
"""

import pandas as pd
import great_expectations as ge
from great_expectations.data_context import get_context
from great_expectations.checkpoint import Checkpoint
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

class DataValidator:
    """Validateur de données avec Great Expectations"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or self._get_project_root()
        self.staging_path = os.path.join(self.project_root, 'data', 'staging')
        self.ge_path = os.path.join(self.project_root, 'pipeline', 'great_expectations')
        
        # Configuration du logging
        self.setup_logging()
        
        # Initialiser Great Expectations
        self.setup_great_expectations()
        
    def _get_project_root(self) -> str:
        """Trouve la racine du projet"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(current_dir))
    
    def setup_logging(self):
        """Configure le logging"""
        self.logger = logging.getLogger('DataValidator')
        self.logger.setLevel(logging.INFO)
    
    def setup_great_expectations(self):
        """Initialise Great Expectations"""
        try:
            # Créer le répertoire GE
            os.makedirs(self.ge_path, exist_ok=True)
            
            # Initialiser le context GE si pas déjà fait
            context_path = os.path.join(self.ge_path, 'great_expectations.yml')
            if not os.path.exists(context_path):
                self.logger.info("Initializing Great Expectations context...")
                
                # Créer un contexte Great Expectations basique
                context_config = {
                    'config_version': 4,
                    'plugins_directory': 'plugins/',
                    'evaluation_parameter_store_name': 'evaluation_parameter_store',
                    'validations_store_name': 'validations_store',
                    'expectations_store_name': 'expectations_store',
                    'checkpoint_store_name': 'checkpoint_store',
                    'config_variables_file_path': 'uncommitted/config_variables.yml',
                    'data_docs_sites': {
                        'local_site': {
                            'class_name': 'SiteBuilder',
                            'show_how_to_buttons': True,
                            'store_backend': {
                                'class_name': 'TupleFilesystemStoreBackend',
                                'base_directory': 'uncommitted/data_docs/local_site/'
                            },
                            'site_index_builder': {
                                'class_name': 'DefaultSiteIndexBuilder'
                            }
                        }
                    },
                    'stores': {
                        'expectations_store': {
                            'class_name': 'ExpectationsStore',
                            'store_backend': {
                                'class_name': 'TupleFilesystemStoreBackend',
                                'base_directory': 'expectations/'
                            }
                        },
                        'validations_store': {
                            'class_name': 'ValidationsStore',
                            'store_backend': {
                                'class_name': 'TupleFilesystemStoreBackend',
                                'base_directory': 'uncommitted/validations/'
                            }
                        },
                        'evaluation_parameter_store': {
                            'class_name': 'EvaluationParameterStore'
                        },
                        'checkpoint_store': {
                            'class_name': 'CheckpointStore',
                            'store_backend': {
                                'class_name': 'TupleFilesystemStoreBackend',
                                'base_directory': 'checkpoints/'
                            }
                        }
                    }
                }
                
                # Créer les répertoires nécessaires
                for subdir in ['expectations', 'checkpoints', 'uncommitted/validations', 
                              'uncommitted/data_docs/local_site', 'plugins']:
                    os.makedirs(os.path.join(self.ge_path, subdir), exist_ok=True)
                
                # Sauvegarder la configuration
                import yaml
                with open(context_path, 'w') as f:
                    yaml.dump(context_config, f, default_flow_style=False)
                
                self.logger.info(f"Created GE context at {context_path}")
            
        except Exception as e:
            self.logger.warning(f"Could not setup Great Expectations: {e}")
            self.logger.info("Continuing with basic validation...")
    
    def create_magasins_expectations(self) -> Dict[str, Any]:
        """Crée les expectations pour les données magasins"""
        return {
            'data_asset_name': 'magasins_staging',
            'expectation_suite_name': 'magasins_suite',
            'expectations': [
                {
                    'expectation_type': 'expect_table_row_count_to_be_between',
                    'kwargs': {'min_value': 40, 'max_value': 60}
                },
                {
                    'expectation_type': 'expect_column_to_exist',
                    'kwargs': {'column': 'id_magasin'}
                },
                {
                    'expectation_type': 'expect_column_values_to_be_unique',
                    'kwargs': {'column': 'id_magasin'}
                },
                {
                    'expectation_type': 'expect_column_values_to_not_be_null',
                    'kwargs': {'column': 'ville'}
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'latitude',
                        'min_value': 41.0,
                        'max_value': 51.0
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'longitude', 
                        'min_value': -5.0,
                        'max_value': 10.0
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_of_type',
                    'kwargs': {
                        'column': 'ca_annuel',
                        'type_': 'float64'
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'ca_annuel',
                        'min_value': 100000,
                        'max_value': 10000000
                    }
                }
            ]
        }
    
    def create_transactions_expectations(self) -> Dict[str, Any]:
        """Crée les expectations pour les transactions"""
        return {
            'data_asset_name': 'transactions_staging',
            'expectation_suite_name': 'transactions_suite',
            'expectations': [
                {
                    'expectation_type': 'expect_table_row_count_to_be_between',
                    'kwargs': {'min_value': 4000, 'max_value': 6000}
                },
                {
                    'expectation_type': 'expect_column_values_to_be_unique',
                    'kwargs': {'column': 'transaction_id'}
                },
                {
                    'expectation_type': 'expect_column_values_to_not_be_null',
                    'kwargs': {'column': 'date'}
                },
                {
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': 'montant',
                        'min_value': 0,
                        'max_value': 1000
                    }
                },
                {
                    'expectation_type': 'expect_column_values_to_not_be_null',
                    'kwargs': {'column': 'magasin_id'}
                },
                {
                    'expectation_type': 'expect_column_values_to_not_be_null',
                    'kwargs': {'column': 'categorie'}
                }
            ]
        }
    
    def validate_basic_expectations(self, df: pd.DataFrame, expectations: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les expectations basiques sans Great Expectations"""
        results = {
            'dataset': expectations['data_asset_name'],
            'suite_name': expectations['expectation_suite_name'],
            'validation_time': datetime.now().isoformat(),
            'success': True,
            'results': []
        }
        
        total_tests = len(expectations['expectations'])
        passed_tests = 0
        
        for expectation in expectations['expectations']:
            exp_type = expectation['expectation_type']
            kwargs = expectation['kwargs']
            
            test_result = {
                'expectation_type': exp_type,
                'kwargs': kwargs,
                'success': False,
                'result': {}
            }
            
            try:
                if exp_type == 'expect_table_row_count_to_be_between':
                    row_count = len(df)
                    min_val = kwargs.get('min_value', 0)
                    max_val = kwargs.get('max_value', float('inf'))
                    test_result['success'] = min_val <= row_count <= max_val
                    test_result['result'] = {'observed_value': row_count}
                
                elif exp_type == 'expect_column_to_exist':
                    column = kwargs['column']
                    test_result['success'] = column in df.columns
                    test_result['result'] = {'observed_value': column in df.columns}
                
                elif exp_type == 'expect_column_values_to_be_unique':
                    column = kwargs['column']
                    if column in df.columns:
                        unique_count = df[column].nunique()
                        total_count = len(df[column].dropna())
                        test_result['success'] = unique_count == total_count
                        test_result['result'] = {
                            'observed_value': unique_count,
                            'total_count': total_count
                        }
                
                elif exp_type == 'expect_column_values_to_not_be_null':
                    column = kwargs['column']
                    if column in df.columns:
                        null_count = df[column].isnull().sum()
                        test_result['success'] = null_count == 0
                        test_result['result'] = {'observed_value': null_count}
                
                elif exp_type == 'expect_column_values_to_be_between':
                    column = kwargs['column']
                    if column in df.columns and df[column].dtype in ['int64', 'float64']:
                        min_val = kwargs.get('min_value', float('-inf'))
                        max_val = kwargs.get('max_value', float('inf'))
                        
                        valid_values = df[column].dropna()
                        within_range = ((valid_values >= min_val) & (valid_values <= max_val)).sum()
                        total_values = len(valid_values)
                        
                        test_result['success'] = within_range == total_values
                        test_result['result'] = {
                            'observed_value': within_range / total_values if total_values > 0 else 0,
                            'within_range': within_range,
                            'total_values': total_values
                        }
                
                elif exp_type == 'expect_column_values_to_be_of_type':
                    column = kwargs['column']
                    expected_type = kwargs['type_']
                    if column in df.columns:
                        actual_type = str(df[column].dtype)
                        test_result['success'] = actual_type == expected_type
                        test_result['result'] = {
                            'observed_value': actual_type,
                            'expected_value': expected_type
                        }
                
                if test_result['success']:
                    passed_tests += 1
                
            except Exception as e:
                test_result['result'] = {'error': str(e)}
                self.logger.warning(f"Test failed with error: {e}")
            
            results['results'].append(test_result)
        
        results['success'] = passed_tests == total_tests
        results['statistics'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests / total_tests * 100 if total_tests > 0 else 0
        }
        
        return results
    
    def validate_all_data(self) -> Dict[str, Any]:
        """Valide toutes les données en staging"""
        self.logger.info("Starting data validation...")
        
        validation_results = {}
        
        # Valider les magasins
        magasins_file = os.path.join(self.staging_path, 'magasins_staging.csv')
        if os.path.exists(magasins_file):
            df_magasins = pd.read_csv(magasins_file)
            magasins_expectations = self.create_magasins_expectations()
            validation_results['magasins'] = self.validate_basic_expectations(
                df_magasins, magasins_expectations
            )
            self.logger.info(f"Magasins validation: {validation_results['magasins']['statistics']['success_rate']:.1f}% passed")
        
        # Valider les transactions
        transactions_file = os.path.join(self.staging_path, 'transactions_staging.csv')
        if os.path.exists(transactions_file):
            df_transactions = pd.read_csv(transactions_file)
            transactions_expectations = self.create_transactions_expectations()
            validation_results['transactions'] = self.validate_basic_expectations(
                df_transactions, transactions_expectations
            )
            self.logger.info(f"Transactions validation: {validation_results['transactions']['statistics']['success_rate']:.1f}% passed")
        
        # Calculer les statistiques globales
        if validation_results:
            total_tests = sum(r['statistics']['total_tests'] for r in validation_results.values())
            passed_tests = sum(r['statistics']['passed_tests'] for r in validation_results.values())
            
            validation_results['summary'] = {
                'validation_time': datetime.now().isoformat(),
                'datasets_validated': len(validation_results),
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'overall_success_rate': passed_tests / total_tests * 100 if total_tests > 0 else 0,
                'overall_success': passed_tests == total_tests
            }
        
        return validation_results
    
    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Génère un rapport de validation"""
        if not validation_results:
            return "No validation results available."
        
        report = []
        report.append("🔍 DATA VALIDATION REPORT")
        report.append("=" * 50)
        
        if 'summary' in validation_results:
            summary = validation_results['summary']
            report.append(f"Validation Time: {summary['validation_time']}")
            report.append(f"Datasets Validated: {summary['datasets_validated']}")
            report.append(f"Overall Success Rate: {summary['overall_success_rate']:.1f}%")
            report.append("")
        
        for dataset_name, results in validation_results.items():
            if dataset_name == 'summary':
                continue
                
            stats = results['statistics']
            status = "✅ PASSED" if results['success'] else "❌ FAILED"
            
            report.append(f"📊 {dataset_name.upper()} - {status}")
            report.append(f"  Tests: {stats['passed_tests']}/{stats['total_tests']} passed ({stats['success_rate']:.1f}%)")
            
            # Détail des tests échoués
            failed_tests = [r for r in results['results'] if not r['success']]
            if failed_tests:
                report.append("  Failed tests:")
                for test in failed_tests:
                    report.append(f"    - {test['expectation_type']}: {test.get('result', {})}")
            
            report.append("")
        
        report_text = "\n".join(report)
        
        # Sauvegarder le rapport
        reports_dir = os.path.join(self.project_root, 'pipeline', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        report_path = os.path.join(reports_dir, 
                                  f'validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        # Sauvegarder aussi en JSON
        json_path = os.path.join(reports_dir, 
                                f'validation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, indent=2, default=str)
        
        self.logger.info(f"Validation report saved to {report_path}")
        
        return report_text
    
    def run_validation_pipeline(self):
        """Exécute le pipeline complet de validation"""
        self.logger.info("Running data validation pipeline...")
        
        try:
            # Valider les données
            validation_results = self.validate_all_data()
            
            # Générer le rapport
            report = self.generate_validation_report(validation_results)
            print(report)
            
            # Retourner les résultats
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Validation pipeline failed: {e}")
            raise

if __name__ == "__main__":
    validator = DataValidator()
    results = validator.run_validation_pipeline()