# Installation complète du projet Retail Geodata Case
# Script PowerShell pour automatiser l'installation

Write-Host "🚀 Installation Retail Geodata Case" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Vérification Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé. Veuillez installer Python d'abord." -ForegroundColor Red
    exit 1
}

# Installation des dépendances
Write-Host "`n📦 Installation des dépendances..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de l'installation des dépendances" -ForegroundColor Red
    exit 1
}

# Génération des données
Write-Host "`n📊 Génération des données de démonstration..." -ForegroundColor Yellow
Set-Location scripts
python generate_data.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la génération des données" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

# Test du modèle
Write-Host "`n🤖 Test du modèle prédictif..." -ForegroundColor Yellow
Set-Location scripts
python ca_predictor.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Erreur lors du test du modèle (optionnel)" -ForegroundColor Yellow
}

Set-Location ..

Write-Host "`n✅ Installation terminée avec succès!" -ForegroundColor Green
Write-Host "`n🎯 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "1. Explorer le notebook: jupyter notebook notebooks/01_analyse_exploratoire.ipynb" -ForegroundColor White
Write-Host "2. Lancer le dashboard: streamlit run dashboard/app.py" -ForegroundColor White
Write-Host "3. Analyser les résultats dans data/" -ForegroundColor White

Write-Host "`n📁 Structure créée:" -ForegroundColor Cyan
Get-ChildItem -Recurse -Directory | Select-Object Name | Format-Table -AutoSize