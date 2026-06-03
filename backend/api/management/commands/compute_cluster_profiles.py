"""
Calcule le profil dominant de chaque cluster (mode des features + médiane vma)
et remplit ClusterDepartement.recommandation.

Les clusters étant globaux, le profil est identique pour tous les départements
d'un même (model_name, cluster_number).

Usage :
    python manage.py compute_cluster_profiles
"""

import os
import sqlite3

import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand

from api.models import ClusterDepartement

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH      = os.path.join(_BACKEND_DIR, 'db.sqlite3')
LABELLED_CSV = os.path.join(_BACKEND_DIR, 'data', 'accidents_labelled.csv')

MODELS = [
    ('kmeans',    'cluster_kmeans'),
    ('bisecting', 'cluster_bisecting'),
    ('gmm',       'cluster_gmm'),
]

# Abréviations pour garder les descriptions compactes dans l'UI
_ABBREV = {
    'En agglomération':                            'En agglo',
    'Hors agglomération':                          'Hors agglo',
    'Crépuscule ou aube':                          'Crépuscule',
    'Nuit sans éclairage public':                  'Nuit sans éclairage',
    'Nuit avec éclairage public allumé':           'Nuit éclairée',
    'Nuit avec éclairage public non allumé':       'Nuit non éclairée',
    'Route Départementale':                        'Route dép.',
    'Voie Communales':                             'Voie communale',
    'Route nationale':                             'Route nat.',
    'Parc de stationnement ouvert à la circulation publique': 'Parking',
    'Routes de métropole urbaine':                 'Voie urbaine',
    'Hors réseau public':                          'Hors réseau',
    'VU seul 1,5T <= PTAC <= 3,5T':               'Véhicule utilitaire',
    'PL seul 3,5T <PTCA <= 7,5T':                 'Poids lourd',
    'PL seul > 7,5T':                             'Poids lourd',
    'PL > 3,5T + remorque':                       'PL + remorque',
    'Tracteur routier seul':                       'Tracteur routier',
    'Tracteur routier + semi-remorque':            'Semi-remorque',
    'Cyclomoteur <50cm3':                          'Cyclomoteur',
    'Scooter < 50 cm3':                           'Scooter',
    'Motocyclette > 50 cm3 et <= 125 cm3':        'Moto ≤125cm3',
    'Motocyclette > 125 cm3':                     'Moto >125cm3',
    'Scooter > 50 cm3 et <= 125 cm3':             'Scooter ≤125cm3',
    'Scooter > 125 cm3':                          'Scooter >125cm3',
    'EDP à moteur':                               'Trottinette',
    'EDP sans moteur':                            'Trottinette',
}

_SQL = """
SELECT a.Num_Acc, a.lum, a.atm, a.agg,
       l.catr, l.vma,
       v.catv
FROM   api_accident a
LEFT JOIN (SELECT Num_Acc, catr, vma FROM api_lieu     GROUP BY Num_Acc) l ON a.Num_Acc = l.Num_Acc
LEFT JOIN (SELECT Num_Acc, catv      FROM api_vehicule GROUP BY Num_Acc) v ON a.Num_Acc = v.Num_Acc
"""


def _abbrev(val):
    if pd.isna(val) or val == '':
        return None
    return _ABBREV.get(str(val), str(val))


def _mode(series):
    clean = series.replace('', np.nan).dropna()
    return clean.mode().iloc[0] if not clean.empty else None


class Command(BaseCommand):
    help = "Remplit ClusterDepartement.recommandation avec le profil dominant de chaque cluster."

    def handle(self, *args, **options):
        self.stdout.write("Chargement des données...")
        conn        = sqlite3.connect(DB_PATH)
        df_acc      = pd.read_sql_query(_SQL, conn)
        conn.close()
        df_labels   = pd.read_csv(LABELLED_CSV, usecols=['Num_Acc', 'cluster_kmeans', 'cluster_bisecting', 'cluster_gmm'])
        df          = df_acc.merge(df_labels, on='Num_Acc', how='inner')
        self.stdout.write(f"  {len(df):,} accidents chargés\n")

        total_updated = 0

        for model_name, cluster_col in MODELS:
            self.stdout.write(f"{model_name}")

            for k in sorted(df[cluster_col].dropna().unique()):
                subset = df[df[cluster_col] == k]

                parts = []

                for feat in ['lum', 'atm', 'agg', 'catr', 'catv']:
                    val = _mode(subset[feat])
                    short = _abbrev(val)
                    if short:
                        parts.append(short)

                # vma : médiane en excluant les valeurs aberrantes (-1, 0, >200)
                vma_vals = pd.to_numeric(subset['vma'], errors='coerce')
                vma_vals = vma_vals[(vma_vals > 0) & (vma_vals <= 200)]
                if not vma_vals.empty:
                    parts.append(f"{int(vma_vals.median())} km/h")

                desc = ' · '.join(parts)
                n = ClusterDepartement.objects.filter(
                    model_name=model_name,
                    cluster_number=int(k),
                ).update(recommandation=desc)

                total_updated += n
                self.stdout.write(f"  Cluster {int(k)} ({n} dpts) : {desc}")

        self.stdout.write(self.style.SUCCESS(f"\n{total_updated} enregistrements mis à jour."))
