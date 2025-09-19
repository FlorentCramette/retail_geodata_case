"""
Script pour corriger les doublons d'enseignes avec espaces
"""
import pandas as pd
import os

def fix_enseigne_duplicates():
    """Corrige les doublons d'enseignes causés par des espaces"""
    
    # Chemin des fichiers
    processed_file = 'data/processed/magasins_performance.csv'
    raw_file = 'data/magasins_performance.csv'
    
    # Déterminer quel fichier utiliser
    if os.path.exists(processed_file):
        file_path = processed_file
        print(f"📂 Correction du fichier processed: {file_path}")
    else:
        file_path = raw_file
        print(f"📂 Correction du fichier raw: {file_path}")
    
    # Charger les données
    df = pd.read_csv(file_path)
    
    print(f"🔍 Données avant correction:")
    print(f"   - Nombre total de magasins: {len(df)}")
    print(f"   - Enseignes uniques: {df['enseigne'].nunique()}")
    print("   - Distribution des enseignes:")
    for enseigne, count in df['enseigne'].value_counts().items():
        print(f"     '{enseigne}': {count}")
    
    # Nettoyer les enseignes (supprimer espaces début/fin)
    df['enseigne'] = df['enseigne'].str.strip()
    
    print(f"\n✅ Données après correction:")
    print(f"   - Nombre total de magasins: {len(df)}")
    print(f"   - Enseignes uniques: {df['enseigne'].nunique()}")
    print("   - Distribution des enseignes:")
    for enseigne, count in df['enseigne'].value_counts().items():
        print(f"     '{enseigne}': {count}")
    
    # Sauvegarder le fichier corrigé
    df.to_csv(file_path, index=False)
    print(f"\n💾 Fichier sauvegardé: {file_path}")
    
    return df

if __name__ == "__main__":
    fix_enseigne_duplicates()