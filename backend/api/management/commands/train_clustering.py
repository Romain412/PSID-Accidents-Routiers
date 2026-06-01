"""
Entraîne les 3 modèles de clustering (K=5) sur le dataset BAAC 2024
et affiche la répartition des accidents par cluster.

Usage :
    python manage.py train_clustering
"""

import os

import joblib
import numpy as np
from django.core.management.base import BaseCommand
from sklearn.cluster import BisectingKMeans, KMeans
from sklearn.mixture import GaussianMixture

from api.preprocessing import (
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    charger_dataframe,
    construire_preprocesseur,
)

# __file__ : backend/api/management/commands/train_clustering.py
# dirname ×4 : backend/
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_DIR     = os.path.join(_BACKEND_DIR, 'data')
MODELS_DIR   = os.path.join(DATA_DIR, 'models')

N_CLUSTERS = 5


class Command(BaseCommand):
    help = "Entraîne K-Means, Bisecting K-Means et GMM (K=5) sur les données BAAC 2024"

    # ── helpers ──────────────────────────────────────────────────────────────

    def _section(self, titre):
        self.stdout.write(f"\n{'─' * 50}")
        self.stdout.write(self.style.HTTP_INFO(f"  {titre}"))
        self.stdout.write(f"{'─' * 50}")

    def _repartition(self, df, col):
        total = len(df)
        for k, n in df[col].value_counts().sort_index().items():
            self.stdout.write(f"    Cluster {k} : {n:>6,} accidents  ({n / total * 100:5.1f} %)")

    # ── commande principale ───────────────────────────────────────────────────

    def handle(self, *args, **options):

        # 1. Chargement ───────────────────────────────────────────────────────
        self._section("Chargement et pré-traitement")
        df  = charger_dataframe()
        pre = construire_preprocesseur()
        X   = pre.fit_transform(df[CATEGORICAL_FEATURES + NUMERICAL_FEATURES])
        self.stdout.write(f"  Accidents chargés : {len(df):,}")
        self.stdout.write(f"  Dimensions X      : {X.shape}")

        # 2. K-Means ──────────────────────────────────────────────────────────
        self._section("K-Means  (n_clusters=5, random_state=42)")
        km = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init="auto")
        df["cluster_kmeans"] = km.fit_predict(X)
        self.stdout.write(f"  Inertie (WCSS) : {km.inertia_:,.1f}")
        self._repartition(df, "cluster_kmeans")

        # 3. Bisecting K-Means ────────────────────────────────────────────────
        self._section("Bisecting K-Means  (n_clusters=5, random_state=42)")
        bkm = BisectingKMeans(n_clusters=N_CLUSTERS, random_state=42)
        df["cluster_bisecting"] = bkm.fit_predict(X)
        self.stdout.write(f"  Inertie (WCSS) : {bkm.inertia_:,.1f}")
        self._repartition(df, "cluster_bisecting")

        # 4. Gaussian Mixture Model ───────────────────────────────────────────
        self._section("Gaussian Mixture Model  (n_components=5, random_state=42)")
        gmm = GaussianMixture(n_components=N_CLUSTERS, random_state=42)
        gmm.fit(X)
        df["cluster_gmm"] = gmm.predict(X)
        self.stdout.write(f"  Log-vraisemblance (lower bound) : {gmm.lower_bound_:,.4f}")
        self._repartition(df, "cluster_gmm")

        # 5. Sauvegarde ───────────────────────────────────────────────────────
        self._section("Sauvegarde")

        joblib.dump(pre,  os.path.join(MODELS_DIR, 'preprocesseur.pkl'))
        joblib.dump(km,   os.path.join(MODELS_DIR, 'kmeans.pkl'))
        joblib.dump(bkm,  os.path.join(MODELS_DIR, 'bisecting_kmeans.pkl'))
        joblib.dump(gmm,  os.path.join(MODELS_DIR, 'gmm.pkl'))

        labelled_path = os.path.join(DATA_DIR, 'accidents_labelled.csv')
        df[['Num_Acc', 'dep', 'cluster_kmeans', 'cluster_bisecting', 'cluster_gmm']].to_csv(
            labelled_path, index=False
        )

        self.stdout.write(f"  Modèles   → {MODELS_DIR}/")
        self.stdout.write(f"  Labels    → {labelled_path}")
        self.stdout.write(f"\n{'─' * 50}")
        self.stdout.write(self.style.SUCCESS("  Entraînement terminé."))
        self.stdout.write(f"{'─' * 50}\n")
