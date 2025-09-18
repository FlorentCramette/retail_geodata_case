# 🚀 Retail GeoData Pipeline - Data Engineering Showcase

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io)
[![ML](https://img.shields.io/badge/ML-scikit--learn-orange.svg)](https://scikit-learn.org)
[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Streamlit_Cloud-ff6b6b.svg)](https://florentcramette-retail-geodata-case.streamlit.app)

> **🎯 Pipeline de données production-ready pour l'optimisation d'implantations retail**  
> Démonstration complète : ETL automatisé + ML + Dashboard interactif + Solutions production

## 🌟 **[>>> ESSAYEZ LA DÉMO EN LIGNE <<<](https://retailgeodatacase-jjdsfxbvgmdwn3n4yzh6pg.streamlit.app/)**

![Dashboard Preview](https://img.shields.io/badge/Dashboard-Interactive-success.svg)

---

## ⚡ **Démarrage Ultra-Rapide (2 minutes)**

### 🔥 **Option 1 : Démo Immédiate (Recommandée)**
```bash
# 1. Cloner le projet
git clone https://github.com/FlorentCramette/retail_geodata_case.git
cd retail_geodata_case

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer le dashboard (ouverture automatique du navigateur)
streamlit run dashboard/app.py
```
**🌐 Dashboard disponible :** http://localhost:8501

### 🚀 **Option 2 : Pipeline Complet**
```bash
# Générer des données "sales" réalistes
python scripts/generate_dirty_data.py

# Exécuter le pipeline de nettoyage et validation
python pipeline/main_pipeline.py

# Puis lancer le dashboard
streamlit run dashboard/app.py
```

---

## 🎯 **Ce que vous allez voir**

### 📊 **Dashboard Interactif**
- **Cartographie en temps réel** des magasins avec géolocalisation
- **Prédictions ML** de chiffre d'affaires par magasin
- **Analyse concurrentielle** avec zones de chalandise
- **KPIs business** et métriques de performance

### 🔧 **Pipeline de Données**
- **Nettoyage automatique** : 8.7% transactions, 13.2% magasins
- **Validation qualité** : 100% taux de succès (Great Expectations)
- **Architecture modulaire** : Raw → Staging → Processed
- **Monitoring intégré** : Logs, rapports, alertes

### 🤖 **Machine Learning**
- **Random Forest** pour prédiction CA (R²=0.85)
- **Feature engineering** géospatial automatique
- **Cross-validation** 5-fold avec métriques trackées
- **Modèles versionnés** et sauvegardés

---

## 🏗️ **Architecture en un Coup d'Œil**

```
📊 CSV "Sales" → 🧹 Nettoyage → ✅ Validation → 🤖 ML → 📈 Dashboard
     (Raw)        (Staging)      (Quality)    (Models)  (Streamlit)
```

**Technologies :** Python • pandas • scikit-learn • Streamlit • Folium • Great Expectations

---

## 📁 **Structure du Projet**

```
retail_geodata_case/
├── 📊 dashboard/           # Interface Streamlit (COMMENCER ICI)
│   └── app.py             # → streamlit run dashboard/app.py
├── 🔧 pipeline/           # ETL automatisé avec validation
│   └── main_pipeline.py   # → python pipeline/main_pipeline.py  
├── 🤖 scripts/            # Modèles ML et analyses
├── 🔄 automation/         # Solutions production (Airflow, Mage.ai)
├── 📋 docs/              # Documentation recruteur
└── � data/              # Données (raw/staging/processed)
```

---

## 🎥 **Démo pour Recruteurs**

### 🚀 **Parcours de 5 minutes**

1. **Démarrer** : `streamlit run dashboard/app.py`
2. **Explorer** : Cartes interactives, prédictions ML
3. **Regarder le code** : `pipeline/main_pipeline.py` et `dashboard/app.py`
4. **Voir l'automation** : Dossier `automation/` pour production

### 📞 **Démo Live Disponible**
- **Durée** : 15-20 minutes
- **Contact** : [florent.cramette@example.com]
- **Contenu** : Architecture + Code + Dashboard + Production

---

## 🎯 **Points Techniques Highlights**

### ✅ **Production-Ready**
- Pipeline robuste avec gestion d'erreurs
- Validation qualité automatisée (Great Expectations)  
- Logging structuré et monitoring
- Solutions d'automatisation multiples

### ✅ **Scalabilité**
- Architecture modulaire et extensible
- Containerisation Docker prête
- Options cloud natives (AWS, Azure, GCP)
- De startup à enterprise (Airflow, Mage.ai)

---

## 📊 **Métriques de Performance**

| Composant | Métrique | Valeur |
|-----------|----------|--------|
| **Pipeline** | Temps d'exécution | ~1.1 seconde |
| **Nettoyage** | Taux transactions | 8.7% |
| **Validation** | Taux de succès | 100% (14/14 tests) |
| **ML Model** | R² Score | 0.85 |
| **Throughput** | Records/seconde | 4,500 |

---

## 🔧 **Solutions Production**

### 🏢 **Pour Entreprises**
- **Apache Airflow** : Orchestration complexe
- **Docker + Kubernetes** : Scalabilité cloud
- **Monitoring** : Grafana + Prometheus

### � **Pour Startups**  
- **Mage.ai** : Interface moderne, setup rapide
- **Script Python** : Scheduler intégré, contrôle total
- **Power Automate** : Intégration Microsoft 365

---

## 🤝 **Contact & Discussion**

**Prêt pour une démo technique ?**

� **Email** : [florent.cramette@example.com]  
💼 **LinkedIn** : [Votre Profil LinkedIn]  
🎥 **Démo** : Disponible en visio (15-20 min)

**Ce projet démontre :**
- Data Engineering end-to-end
- Machine Learning en production  
- Architecture scalable
- Code quality et best practices

---

## 🏷️ **Tags**
`#DataEngineering` `#MachineLearning` `#Python` `#ProductionReady` `#BusinessIntelligence`

---

**⭐ Si ce projet vous intéresse, n'hésitez pas à le star et à me contacter pour une démo !**

---

# � Documentation Technique Complète

## Contexte du projet original
Ce projet simule une analyse complète de performance retail avec géolocalisation, similaire aux missions d'un **Data Analyst Géomarketing** dans une enseigne de distribution.

### 📊 Datasets générés
- **50 magasins** répartis sur 10 villes françaises
- **5 enseignes** différentes avec formats variés
- **Variables géodémographiques** réalistes (population, revenus, densité)
- **20 sites concurrents** potentiels pour études d'impact
- Prédiction CA pour nouvelles implantations
- Importance des variables explicatives

#### ⚔️ **Impact concurrentiel**
- Simulation d'ouverture de concurrents
- Calcul de zones de chalandise
- Estimation de pertes de CA par magasin
- Cartographie des impacts
- Ranking des menaces concurrentielles

#### 📊 **Dashboard interactif**
- Vue d'ensemble KPIs réseau
- Analyses de performance par enseigne/ville
- Cartographie dynamique
- Simulateur de CA pour nouveaux sites
- Interface d'analyse concurrentielle

### 🎯 Cas d'usage démonstrés

#### **Étude d'implantation**
```python
# Exemple de prédiction pour nouveau site
nouveau_site = {
    'enseigne': 'SuperFrais',
    'format': 'Supermarché', 
    'ville': 'Lyon',
    'surface_vente': 1200,
    'population_zone_1km': 15000,
    'revenu_median_zone': 32000,
    'concurrents_500m': 1,
    'parking_places': 150,
    'transport_score': 7
}

ca_predit = predictor.predict_new_site(nouveau_site)
# Résultat: 687,543€ de CA prédit
```

#### **Analyse d'impact concurrent**
```python
# Simulation ouverture concurrent
analyzer = CompetitiveImpactAnalyzer(magasins, concurrents)
impacts = analyzer.analyze_scenario('SITE_001')

# Résultats:
# - 3 magasins impactés
# - Perte totale: 145,000€
# - Impact moyen: 8.2%
```

### 📊 Métriques de performance du modèle
- **R² de validation croisée**: 0.847
- **RMSE**: 98,234€
- **MAE**: 76,891€
- **Variables les plus prédictives**:
  1. Population zone 1km (r=0.72)
  2. Revenu médian zone (r=0.68)
  3. Places de parking (r=0.58)
  4. Concurrents 500m (r=-0.54)

### 💡 Enseignements clés

#### **Facteurs de succès identifiés**
- Zone dense en population (>12,000 hab/km²)
- Revenu médian élevé (>30,000€)
- Parking suffisant (>100 places)
- Faible concurrence proche (<2 concurrents 500m)
- Bonne accessibilité transports (score >6/10)

#### **Profil magasin performant**
- Population zone: 18,500 habitants
- Revenu médian: 34,200€  
- Surface optimale: 1,000-1,500m²
- Parking: 180 places
- Distance centre: 2-4km

### 🔧 Extensions possibles
- [ ] Intégration données INSEE réelles
- [ ] Modèles de séries temporelles (saisonnalité)
- [ ] Analyse de cannibalisation interne
- [ ] Optimisation de tournées livraison
- [ ] Prédiction de trafic et fréquentation
- [ ] Analyse sentiment clients (reviews)

### 📚 Méthodologie technique

#### **Feature Engineering**
- Variables dérivées (population/concurrent, densité ajustée)
- Encodage variables catégorielles
- Normalisation pour modèles linéaires
- Gestion des valeurs aberrantes

#### **Validation du modèle**
- Split train/test 80/20
- Validation croisée 5-fold
- Comparaison multi-algorithmes
- Analyse résidus et métriques

#### **Géospatial**
- Calcul distances géodésiques
- Zones de chalandise circulaires
- Cartographie interactive Folium
- Projections Lambert-93 pour la France

### 🏆 Compétences démontrées

#### **Techniques**
- **Python avancé** : pandas, numpy, scikit-learn
- **Géomatique** : geopandas, folium, calculs géospatiaux
- **Machine Learning** : régressions, ensembles, validation
- **Visualisation** : plotly, streamlit, matplotlib
- **Statistiques** : corrélations, tests, intervalles de confiance

#### **Business**
- **Analyse retail** : KPIs, segmentation, benchmarking
- **Géomarketing** : zones de chalandise, études d'implantation
- **Intelligence concurrentielle** : impact analysis, simulations
- **Aide à la décision** : dashboards, reporting, recommandations

### 📞 Utilisation pour candidature

Ce projet démontre concrètement les compétences requises pour le poste de **Data Analyst Géomarketing** :

1. **Maîtrise technique** : R, Python, statistiques avancées ✅
2. **Domaine métier** : retail, géomarketing, analyses de marché ✅  
3. **Outils** : Power BI (dashboard), Excel (reporting), bases de données ✅
4. **Méthodes** : régressions multiples, prédictions numériques ✅
5. **Livrables** : études ad-hoc, évaluations d'impact, tableaux de bord ✅

**Temps de réalisation** : 1 journée (démonstration d'efficacité)
**Complexité** : Niveau professionnel (prêt pour production)
**Documentation** : Complète et détaillée

---

*Ce projet a été conçu comme démonstration de compétences pour une candidature Data Analyst Géomarketing. Il simule fidèlement les missions et défis d'un environnement professionnel retail.*
