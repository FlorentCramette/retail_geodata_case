"""
Modèle prédictif de Chiffre d'Affaires
Régression multiple avec variables géodémographiques
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

class CAPredictor:
    """Modèle de prédiction du Chiffre d'Affaires"""
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.best_model = None
        self.best_score = 0
        
    def prepare_features(self, df):
        """Prépare les features pour la modélisation"""
        
        data = df.copy()
        
        # Gestion des valeurs manquantes
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].median())
        
        # Variables numériques
        numeric_features = ['surface_vente', 'effectif', 'population_zone_1km', 
                          'densite_hab_km2', 'revenu_median_zone', 'age_moyen_zone',
                          'concurrents_500m', 'concurrents_1km', 'parking_places',
                          'distance_centre_ville', 'transport_score']
        
        # Variables catégorielles à encoder
        categorical_features = ['enseigne', 'format', 'ville']
        
        # Encodage des variables catégorielles
        for feature in categorical_features:
            if feature not in self.label_encoders:
                self.label_encoders[feature] = LabelEncoder()
                self.label_encoders[feature].fit(data[feature])
            
            if feature in data.columns:
                data[f'{feature}_encoded'] = self.label_encoders[feature].transform(data[feature])
        
        # Variables dérivées (feature engineering)
        data['population_par_concurrent'] = data['population_zone_1km'] / (data['concurrents_500m'] + 1)
        data['revenu_x_population'] = data['revenu_median_zone'] * data['population_zone_1km'] / 1000000
        data['surface_par_employe'] = data['surface_vente'] / data['effectif']
        data['densite_ajustee'] = data['densite_hab_km2'] / (data['distance_centre_ville'] + 1)
        data['score_accessibilite'] = data['transport_score'] * data['parking_places'] / 100
        data['zone_commerciale_num'] = data['zone_commerciale'].astype(int)
        
        # Variables temporelles
        data['date_ouverture'] = pd.to_datetime(data['date_ouverture'])
        data['anciennete_mois'] = (pd.Timestamp.now() - data['date_ouverture']).dt.days / 30.44
        
        # Sélection des features finales
        feature_columns = (numeric_features + 
                          [f'{f}_encoded' for f in categorical_features] +
                          ['population_par_concurrent', 'revenu_x_population', 
                           'surface_par_employe', 'densite_ajustee', 'score_accessibilite',
                           'zone_commerciale_num', 'anciennete_mois'])
        
        self.feature_names = feature_columns
        return data[feature_columns]
    
    def train_models(self, df, target='ca_annuel'):
        """Entraîne plusieurs modèles et sélectionne le meilleur"""
        
        # Préparation des données
        X = self.prepare_features(df)
        y = df[target]
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normalisation
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Définition des modèles
        models_config = {
            'Linear_Regression': LinearRegression(),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=1.0),
            'Random_Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient_Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        results = {}
        
        print("🤖 Entraînement des modèles...")
        print("="*50)
        
        for name, model in models_config.items():
            # Utiliser les données normalisées pour les modèles linéaires
            if name in ['Linear_Regression', 'Ridge', 'Lasso']:
                X_train_model = X_train_scaled
                X_test_model = X_test_scaled
            else:
                X_train_model = X_train
                X_test_model = X_test
            
            # Entraînement
            model.fit(X_train_model, y_train)
            
            # Prédictions
            y_pred_train = model.predict(X_train_model)
            y_pred_test = model.predict(X_test_model)
            
            # Métriques
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            
            # Validation croisée
            cv_scores = cross_val_score(model, X_train_model, y_train, cv=5, scoring='r2')
            
            results[name] = {
                'model': model,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'mae': test_mae,
                'rmse': test_rmse
            }
            
            print(f"{name}:")
            print(f"  R² train: {train_r2:.3f}")
            print(f"  R² test:  {test_r2:.3f}")
            print(f"  CV R²:    {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
            print(f"  MAE:      {test_mae:,.0f}€")
            print(f"  RMSE:     {test_rmse:,.0f}€")
            print()
        
        # Sélection du meilleur modèle
        best_model_name = max(results.keys(), key=lambda k: results[k]['cv_mean'])
        self.best_model = results[best_model_name]['model']
        self.best_score = results[best_model_name]['cv_mean']
        
        print(f"🏆 Meilleur modèle: {best_model_name} (R² CV: {self.best_score:.3f})")
        
        self.models = results
        return results, X_test, y_test
    
    def analyze_feature_importance(self, df):
        """Analyse l'importance des variables"""
        
        if self.best_model is None:
            print("❌ Aucun modèle entraîné")
            return
        
        # Importance des features (si disponible)
        if hasattr(self.best_model, 'feature_importances_'):
            importance = self.best_model.feature_importances_
            
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            print("📊 Importance des variables:")
            print(feature_importance.head(10))
            
            return feature_importance
        
        elif hasattr(self.best_model, 'coef_'):
            # Coefficients pour modèles linéaires
            coefficients = pd.DataFrame({
                'feature': self.feature_names,
                'coefficient': self.best_model.coef_
            }).sort_values('coefficient', key=abs, ascending=False)
            
            print("📊 Coefficients du modèle:")
            print(coefficients.head(10))
            
            return coefficients
    
    def predict_new_site(self, site_data):
        """Prédit le CA d'un nouveau site"""
        
        if self.best_model is None:
            raise ValueError("Aucun modèle entraîné")
        
        # Préparation des features
        features = self.prepare_features(pd.DataFrame([site_data]))
        
        # Normalisation si nécessaire
        if type(self.best_model).__name__ in ['LinearRegression', 'Ridge', 'Lasso']:
            features_scaled = self.scaler.transform(features)
            prediction = self.best_model.predict(features_scaled)[0]
        else:
            prediction = self.best_model.predict(features)[0]
        
        return prediction
    
    def save_model(self, filepath='../models/ca_predictor.joblib'):
        """Sauvegarde le modèle"""
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'best_model': self.best_model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'best_score': self.best_score
        }
        
        joblib.dump(model_data, filepath)
        print(f"✅ Modèle sauvegardé: {filepath}")


def demo_prediction():
    """Démonstration du modèle"""
    
    print("🚀 DÉMONSTRATION - Modèle prédictif CA")
    print("="*50)
    
    # Chargement des données avec chemin corrigé
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(os.path.dirname(current_dir), 'data', 'magasins_performance.csv')
    
    if not os.path.exists(data_path):
        print(f"❌ Fichier non trouvé: {data_path}")
        return None
        
    df = pd.read_csv(data_path)
    
    # Nettoyage des données NaN
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
    
    print(f"📊 Données chargées: {len(df)} magasins")
    
    # Initialisation et entraînement
    predictor = CAPredictor()
    results, X_test, y_test = predictor.train_models(df)
    
    # Analyse des features
    predictor.analyze_feature_importance(df)
    
    # Sauvegarde
    predictor.save_model()
    
    # Exemple de prédiction pour un nouveau site
    print("\n🎯 Exemple de prédiction:")
    nouveau_site = {
        'enseigne': 'SuperFrais',
        'format': 'Supermarché',
        'ville': 'Lyon',
        'surface_vente': 1200,
        'effectif': 25,
        'population_zone_1km': 15000,
        'densite_hab_km2': 3000,
        'revenu_median_zone': 32000,
        'age_moyen_zone': 38.5,
        'concurrents_500m': 1,
        'concurrents_1km': 3,
        'parking_places': 150,
        'distance_centre_ville': 2.5,
        'transport_score': 7,
        'zone_commerciale': True,
        'date_ouverture': '2024-01-01'
    }
    
    ca_predit = predictor.predict_new_site(nouveau_site)
    print(f"CA prédit: {ca_predit:,.0f}€")
    
    return predictor


if __name__ == "__main__":
    predictor = demo_prediction()