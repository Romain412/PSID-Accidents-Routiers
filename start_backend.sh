#!/bin/bash
# Lance le backend Django (macOS / Linux).
# Les étapes longues sont ignorées si déjà effectuées.

set -e
cd "$(dirname "$0")/backend"

echo "=== Backend Django — PSID Accidents Routiers ==="

# Virtualenv
if [ ! -d "venv" ]; then
    echo "[1/5] Création du virtualenv..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "[1/5] Virtualenv actif."

# Dépendances
echo "[2/5] Installation des dépendances..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Setup + lancement
python _setup.py
