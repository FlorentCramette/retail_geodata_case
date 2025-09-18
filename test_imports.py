#!/usr/bin/env python3
"""
Test rapide des imports pour vérifier que tout fonctionne
"""

import sys
import os

# Ajout du chemin scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_path = os.path.join(current_dir, 'scripts')
sys.path.append(scripts_path)

print("🧪 Test des imports...")

try:
    from ca_predictor_clean import CAPredictor
    print("✅ CAPredictor importé avec succès")
except Exception as e:
    print(f"❌ Erreur CAPredictor: {e}")

try:
    from competitive_analysis_clean import CompetitiveImpactAnalyzer
    print("✅ CompetitiveImpactAnalyzer importé avec succès")
except Exception as e:
    print(f"❌ Erreur CompetitiveImpactAnalyzer: {e}")

try:
    import streamlit as st
    print("✅ Streamlit importé avec succès")
except Exception as e:
    print(f"❌ Erreur Streamlit: {e}")

try:
    import folium
    print("✅ Folium importé avec succès")
except Exception as e:
    print(f"❌ Erreur Folium: {e}")

try:
    import geopy
    print("✅ Geopy importé avec succès")
except Exception as e:
    print(f"❌ Erreur Geopy: {e}")

print("\n🎯 Test terminé !")
print("Si tous les imports sont ✅, le dashboard devrait fonctionner parfaitement.")
print("\n🌐 Accédez au dashboard: http://localhost:8501")
