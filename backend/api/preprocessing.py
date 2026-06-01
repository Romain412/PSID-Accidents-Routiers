"""
Pipeline de pré-traitement commun aux trois modèles de clustering.

Colonnes utilisées
------------------
Catégorielles  : lum, atm, agg   (api_accident)
                 catr             (api_lieu)
                 catv             (api_vehicule)
Numérique      : vma              (api_lieu)
Identifiant    : dep              (api_accident)  — non transformé, sert au groupement

Jointure       : un accident ↔ un lieu (premier lieu par Num_Acc) ↔ un véhicule
                 (premier véhicule par Num_Acc).
                 La valeur sentinelle vma = -1 (BAAC : «non renseigné») est
                 remplacée par NaN avant le scaling.
"""

import os
import sqlite3

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')

CATEGORICAL_FEATURES = ['lum', 'atm', 'agg', 'catr', 'catv']
NUMERICAL_FEATURES   = ['vma']

_SQL = """
SELECT
    a.Num_Acc,
    a.dep,
    a.lum,
    a.atm,
    a.agg,
    l.catr,
    CAST(l.vma  AS REAL) AS vma,
    v.catv
FROM api_accident a
LEFT JOIN (
    SELECT Num_Acc, catr, vma
    FROM   api_lieu
    GROUP  BY Num_Acc
) l ON a.Num_Acc = l.Num_Acc
LEFT JOIN (
    SELECT Num_Acc, catv
    FROM   api_vehicule
    GROUP  BY Num_Acc
) v ON a.Num_Acc = v.Num_Acc
WHERE a.dep IS NOT NULL
  AND a.dep != ''
"""


def charger_dataframe(db_path=DB_PATH):
    """
    Retourne un DataFrame nettoyé avec les colonnes nécessaires au clustering.
    """
    conn = sqlite3.connect(db_path)
    df   = pd.read_sql_query(_SQL, conn)
    conn.close()

    df.replace('', np.nan, inplace=True)

    # vma = -1 signifie "non renseigné" dans le BAAC
    df['vma'] = df['vma'].replace(-1, np.nan)

    return df


def construire_preprocesseur():
    """
    Retourne le ColumnTransformer commun à tous les modèles.

    - OneHotEncoder  : variables catégorielles (lum, atm, agg, catr, catv)
      + SimpleImputer(most_frequent) en amont pour les éventuels NaN
    - StandardScaler : variable numérique (vma)
      + SimpleImputer(median) en amont pour les NaN / sentinelles -1
    """
    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ])

    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler',  StandardScaler()),
    ])

    preprocesseur = ColumnTransformer(
        transformers=[
            ('cat', cat_pipeline, CATEGORICAL_FEATURES),
            ('num', num_pipeline, NUMERICAL_FEATURES),
        ],
        remainder='drop',
    )

    return preprocesseur
