@echo off
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

echo Lancement du dashboard Streamlit...
python -m streamlit run dashboard/app.py --server.headless true

pause
