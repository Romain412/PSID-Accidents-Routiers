"""
Entraîne un Random Forest calibré (CalibratedClassifierCV) pour prédire
la gravité d'un accident (grav) à partir des conditions de conduite.

Grain : un usager par ligne (125 k lignes).
Features : lum, atm, agg, catr, catv, vma, dep.
Target  : grav ∈ {Indemne, Blessé léger, Blessé hospitalisé, Tué}

Usage :
    python manage.py train_simulator
"""

import os
import sqlite3

import joblib
import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

_BACKEND_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH        = os.path.join(_BACKEND_DIR, 'db.sqlite3')
MODEL_OUT      = os.path.join(_BACKEND_DIR, 'data', 'models', 'simulator_model.pkl')

CATEGORICAL = ['lum', 'atm', 'agg', 'catr', 'catv', 'dep']
NUMERICAL   = ['vma']
TARGET      = 'grav'
VALID_GRAV  = ('Indemne', 'Blessé léger', 'Blessé hospitalisé', 'Tué')

_SQL = """
SELECT a.lum, a.atm, a.agg, a.dep,
       l.catr, CAST(l.vma AS REAL) AS vma,
       v.catv,
       u.grav
FROM   api_usager u
JOIN   api_accident a ON u.Num_Acc = a.Num_Acc
LEFT JOIN (SELECT Num_Acc, catr, vma FROM api_lieu     GROUP BY Num_Acc) l ON a.Num_Acc = l.Num_Acc
LEFT JOIN (SELECT Num_Acc, catv      FROM api_vehicule GROUP BY Num_Acc) v ON a.Num_Acc = v.Num_Acc
WHERE  u.grav IN ('Indemne','Blessé léger','Blessé hospitalisé','Tué')
  AND  a.dep IS NOT NULL AND a.dep != ''
"""


class Command(BaseCommand):
    help = 'Entraîne le Random Forest calibré du simulateur de risque.'

    def handle(self, *args, **options):
        # ── 1. Chargement ─────────────────────────────────────────────────────
        self.stdout.write('Chargement des données...')
        conn = sqlite3.connect(DB_PATH)
        df   = pd.read_sql_query(_SQL, conn)
        conn.close()

        df.replace('', np.nan, inplace=True)
        df['vma'] = pd.to_numeric(df['vma'], errors='coerce').replace(-1, np.nan)
        df.dropna(subset=CATEGORICAL + NUMERICAL + [TARGET], inplace=True)

        self.stdout.write(f'  {len(df):,} usagers chargés')
        self.stdout.write('  Distribution :')
        for g, n in df[TARGET].value_counts().items():
            self.stdout.write(f'    {g}: {n:,} ({n/len(df)*100:.1f}%)')

        X = df[CATEGORICAL + NUMERICAL]
        y = df[TARGET]

        # ── 2. Préprocesseur (inclut dep) ──────────────────────────────────────
        cat_pipe = Pipeline([
            ('imp', SimpleImputer(strategy='most_frequent')),
            ('enc', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
        ])
        num_pipe = Pipeline([
            ('imp', SimpleImputer(strategy='median')),
            ('sca', StandardScaler()),
        ])
        preprocesseur = ColumnTransformer([
            ('cat', cat_pipe, CATEGORICAL),
            ('num', num_pipe, NUMERICAL),
        ], remainder='drop')

        # ── 3. Modèle ──────────────────────────────────────────────────────────
        # max_depth=12 : limite les arbres à 4096 feuilles max — modèle ~50-70 Mo
        self.stdout.write('\nEntraînement Random Forest calibré (cv=3, max_depth=12)...')
        rf  = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            random_state=42,
            n_jobs=-1,
        )
        cal = CalibratedClassifierCV(rf, method='sigmoid', cv=3)

        X_t = preprocesseur.fit_transform(X)
        cal.fit(X_t, y)

        self.stdout.write(f'  Classes : {list(cal.classes_)}')

        # ── 4. Sauvegarde ──────────────────────────────────────────────────────
        joblib.dump({'preprocesseur': preprocesseur, 'model': cal}, MODEL_OUT)
        self.stdout.write(self.style.SUCCESS(f'\nModèle sauvegardé : {MODEL_OUT}'))
