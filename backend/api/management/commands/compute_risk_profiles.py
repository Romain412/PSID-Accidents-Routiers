"""
Croise les labels de cluster avec la gravité des usagers (grav) pour
calculer les profils de risque par département et peupler ClusterDepartement.

Dépend de : backend/data/accidents_labelled.csv  (produit par train_clustering)

Usage :
    python manage.py compute_risk_profiles
"""

import os
import sqlite3

import pandas as pd
from django.core.management.base import BaseCommand

from api.models import ClusterDepartement

# ── Chemins ───────────────────────────────────────────────────────────────────
# __file__ : backend/api/management/commands/compute_risk_profiles.py
# dirname ×4 : backend/
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_PATH      = os.path.join(_BACKEND_DIR, 'db.sqlite3')
LABELLED_CSV = os.path.join(_BACKEND_DIR, 'data', 'accidents_labelled.csv')

# ── Mapping gravité → champ Django ───────────────────────────────────────────
GRAV_TO_FIELD = {
    'Indemne':            'pct_indemne',
    'Blessé léger':       'pct_blesse_leger',
    'Blessé hospitalisé': 'pct_blesse_grave',
    'Tué':                'pct_tue',
}
GRAV_COLS = list(GRAV_TO_FIELD.keys())

# ── Modèles à traiter ─────────────────────────────────────────────────────────
MODELS = [
    ('kmeans',    'cluster_kmeans'),
    ('bisecting', 'cluster_bisecting'),
    ('gmm',       'cluster_gmm'),
]


class Command(BaseCommand):
    help = "Peuple ClusterDepartement avec les profils de risque gravité × cluster × département"

    def _section(self, titre):
        self.stdout.write(f"\n{'─' * 52}")
        self.stdout.write(self.style.HTTP_INFO(f"  {titre}"))
        self.stdout.write(f"{'─' * 52}")

    def handle(self, *args, **options):

        # 1. Chargement ───────────────────────────────────────────────────────
        self._section("Chargement")

        df_labels = pd.read_csv(LABELLED_CSV)
        self.stdout.write(f"  Labels chargés    : {len(df_labels):,} accidents")

        conn       = sqlite3.connect(DB_PATH)
        df_usagers = pd.read_sql_query(
            f"""
            SELECT Num_Acc, grav
            FROM   api_usager
            WHERE  grav IN ({', '.join(f"'{g}'" for g in GRAV_COLS)})
            """,
            conn,
        )
        conn.close()
        self.stdout.write(f"  Usagers chargés   : {len(df_usagers):,}")

        # 2. Jointure usagers × labels de cluster ─────────────────────────────
        self._section("Jointure")

        df = df_usagers.merge(
            df_labels[['Num_Acc', 'dep', 'cluster_kmeans', 'cluster_bisecting', 'cluster_gmm']],
            on='Num_Acc',
            how='inner',
        )
        df = df.dropna(subset=['dep'])
        self.stdout.write(f"  Usagers joints    : {len(df):,}")

        # 3. Calcul des profils par modèle ────────────────────────────────────
        self._section("Calcul des profils de risque")

        ClusterDepartement.objects.all().delete()
        self.stdout.write("  Table vidée (réinitialisation propre)")

        all_records = []

        for model_name, cluster_col in MODELS:

            # Comptage par (dep, cluster, grav)
            counts = (
                df.groupby(['dep', cluster_col, 'grav'])
                .size()
                .rename('n')
                .reset_index()
            )

            # Pourcentage au sein de chaque (dep, cluster)
            counts['pct'] = (
                counts['n']
                / counts.groupby(['dep', cluster_col])['n'].transform('sum')
                * 100
            )

            # Pivot : une colonne par niveau de gravité
            # reindex garantit la présence des 4 colonnes même si un niveau est absent
            pivot = (
                counts
                .pivot_table(
                    index=['dep', cluster_col],
                    columns='grav',
                    values='pct',
                    fill_value=0.0,
                )
                .reindex(columns=GRAV_COLS, fill_value=0.0)
                .reset_index()
            )

            records = [
                ClusterDepartement(
                    model_name       = model_name,
                    departement      = str(row['dep']),
                    cluster_number   = int(row[cluster_col]),
                    pct_indemne      = round(row['Indemne'],            2),
                    pct_blesse_leger = round(row['Blessé léger'],       2),
                    pct_blesse_grave = round(row['Blessé hospitalisé'], 2),
                    pct_tue          = round(row['Tué'],                2),
                )
                for _, row in pivot.iterrows()
            ]

            all_records.extend(records)
            self.stdout.write(f"  {model_name:<20} → {len(records):>4} enregistrements")

        # 4. Insertion en base ────────────────────────────────────────────────
        self._section("bulk_create")

        ClusterDepartement.objects.bulk_create(all_records, batch_size=500)
        total = ClusterDepartement.objects.count()

        self.stdout.write(f"\n{'─' * 52}")
        self.stdout.write(self.style.SUCCESS(f"  {total} enregistrements insérés en base."))
        self.stdout.write(f"{'─' * 52}\n")
