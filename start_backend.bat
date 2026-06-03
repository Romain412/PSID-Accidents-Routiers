@echo off
:: Lance le backend Django (Windows).
:: Les etapes longues sont ignorees si deja effectuees.

cd /d "%~dp0backend"
echo === Backend Django - PSID Accidents Routiers ===

:: Virtualenv
if not exist venv (
    echo [1/5] Creation du virtualenv...
    python -m venv venv
)
call venv\Scripts\activate
echo [1/5] Virtualenv actif.

:: Dependances
echo [2/5] Installation des dependances...
pip install --upgrade pip -q
pip install -r requirements.txt -q

:: Setup + lancement
python _setup.py
