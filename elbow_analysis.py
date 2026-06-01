"""
Critère du coude (K-Means) — dataset BAAC 2024 complet.

Calcule le WCSS pour k=2 à 10 sur l'ensemble des accidents
ayant des coordonnées GPS valides et sauvegarde le graphique.

Usage :
    source backend/venv/bin/activate
    python elbow_analysis.py
"""

import os
import sqlite3

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

DB_PATH    = os.path.join(os.path.dirname(__file__), 'backend', 'db.sqlite3')
OUTPUT_PNG = os.path.join(os.path.dirname(__file__), 'elbow_curve.png')


def charger_accidents(db_path):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        """
        SELECT CAST(lat  AS REAL) AS lat,
               CAST(long AS REAL) AS long
        FROM   api_accident
        WHERE  lat  IS NOT NULL
          AND  long IS NOT NULL
          AND  lat  != 0
          AND  long != 0
        """,
        conn,
    )
    conn.close()
    return df


def trouver_k_optimal(df, k_min=2, k_max=10):
    X        = df[['lat', 'long']].values.astype(float)
    k_values = list(range(k_min, k_max + 1))
    wcss     = []

    for k in k_values:
        inertie = KMeans(n_clusters=k, random_state=42, n_init='auto').fit(X).inertia_
        wcss.append(inertie)
        print(f"  k={k:2d}  WCSS = {inertie:>15,.1f}")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(
        k_values, wcss,
        color='#3182CE', linewidth=2.5,
        marker='o', markersize=9,
        markerfacecolor='white', markeredgewidth=2.5,
    )
    ax.set_xlabel('Nombre de clusters (k)', fontsize=12)
    ax.set_ylabel('Inertie (WCSS)', fontsize=12)
    ax.set_title(
        'Critère du coude — Choix optimal de k\n'
        f'K-Means · {len(df):,} accidents · BAAC 2024',
        fontsize=13, fontweight='bold',
    )
    ax.set_xticks(k_values)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=150, bbox_inches='tight')
    plt.close()

    return k_values, wcss


if __name__ == '__main__':
    print(f"Base de données : {DB_PATH}")
    df = charger_accidents(DB_PATH)
    print(f"{len(df):,} accidents chargés (coordonnées valides)\n")

    print("Calcul WCSS pour k = 2 à 10 :")
    trouver_k_optimal(df)

    print(f"\nGraphique sauvegardé : {OUTPUT_PNG}")
