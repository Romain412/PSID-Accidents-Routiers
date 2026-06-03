"""
Script de setup idempotent — appelé par start_backend.sh et start_backend.bat.
Exécute uniquement les étapes nécessaires selon l'état de la base.
"""
import os
import sqlite3
import subprocess
import sys

BASE = os.path.dirname(__file__)
DB   = os.path.join(BASE, 'db.sqlite3')


def run(cmd):
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


def db_count(table):
    if not os.path.exists(DB):
        return 0
    try:
        conn  = sqlite3.connect(DB)
        count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


os.chdir(BASE)

# Migrations
print('[3/5] Migrations...')
run('python manage.py migrate')

# Import CSV
accident_count = db_count('api_accident')
print(f'[4/5] Données : {accident_count:,} accidents en base.')
if accident_count == 0:
    print('      → Import CSV BAAC (quelques minutes)...')
    run('python manage.py import_csv')
else:
    print('      → Import ignoré.')

# Clustering
print('[5/5] Pipeline de clustering...')
models_ok = os.path.exists(os.path.join(BASE, 'data', 'models', 'bisecting_kmeans.pkl'))
if not models_ok:
    print('      → Entraînement des modèles (1-2 min)...')
    run('python manage.py train_clustering')
else:
    print('      → Modèles déjà entraînés, ignoré.')

cd_count = db_count('api_clusterdepartement')
if cd_count == 0:
    print('      → Calcul des profils de risque...')
    run('python manage.py compute_risk_profiles')
    run('python manage.py compute_cluster_profiles')
else:
    print(f'      → Profils déjà calculés ({cd_count} entrées), ignoré.')

sim_model = os.path.join(BASE, 'data', 'models', 'simulator_model.pkl')
if not os.path.exists(sim_model):
    print('      → Entraînement du modèle simulateur (Random Forest, 2-5 min)...')
    run('python manage.py train_simulator')
else:
    print('      → Modèle simulateur déjà entraîné, ignoré.')

print()
print('Serveur disponible sur http://localhost:8000')
print('=' * 45)
run('python manage.py runserver')
