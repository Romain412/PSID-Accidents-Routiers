from django.http import JsonResponse
from .models import Accident, Vehicule, Usager, ClusterDepartement
from django.forms.models import model_to_dict
from django.db.models import ExpressionWrapper, IntegerField, F
from django.db.models.functions import Cast
from django.views.decorators.cache import cache_page
from django.db.models import Count

import json
import os
import requests
import joblib
import numpy as np
import pandas as pd
from shapely.geometry import shape, LineString, Point
from shapely.strtree import STRtree

_MODELS_DIR    = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'models')
_sim_cache     = {}   # cache des modèles chargés pour le simulateur

def _load_sim_model(name):
    if name not in _sim_cache:
        _sim_cache[name] = joblib.load(os.path.join(_MODELS_DIR, f'{name}.pkl'))
    return _sim_cache[name]

_LABELLED_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'accidents_labelled.csv')
_df_labelled     = None   # chargé une seule fois au premier appel
_departments     = None   # liste de (code, nom, geom) — mis en cache au démarrage
_departments_idx = None   # STRtree sur les géométries des départements

def _get_labelled_df():
    global _df_labelled
    if _df_labelled is None:
        try:
            _df_labelled = pd.read_csv(
                _LABELLED_CSV_PATH,
                usecols=['Num_Acc', 'dep', 'cluster_kmeans', 'cluster_bisecting', 'cluster_gmm'],
            )
        except FileNotFoundError:
            _df_labelled = pd.DataFrame()
    return _df_labelled

_DEPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'departements.geojson')
_DEPTS_URL = (
    'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/'
    'departements-version-simplifiee.geojson'
)

def get_status(request):
    try:
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        pending = [str(m) for m, _ in plan]
        return JsonResponse({
            'accidents':           Accident.objects.count(),
            'cluster_departement': ClusterDepartement.objects.count(),
            'migrations_pending':  pending,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_accident_details(request, num_acc):
    try:
        accident = Accident.objects.get(Num_Acc=num_acc)
        caract_data = model_to_dict(accident)
        caract_data['date_formatee'] = f"{accident.jour}/{accident.mois}/{accident.an}"

        data = {
            "caracteristiques": caract_data,
            "lieux": list(accident.lieux.values()),
            "vehicules": list(accident.vehicules.values()),
            "usagers": list(accident.usagers.values())
        }
        return JsonResponse(data)

    except Accident.DoesNotExist:
        return JsonResponse({"erreur": "Cet accident n'existe pas dans la base de données."}, status=404)

@cache_page(60 * 60 * 24)
def get_all_locations(request):
    """
    Renvoie uniquement les coordonnées pour alléger le chargement de la carte.
    """
    rows = (
        Accident.objects
        .filter(lat__isnull=False, long__isnull=False)
        .values('Num_Acc', 'lat', 'long')[:4000]
    )
    data = [{"id": r['Num_Acc'], "lat": float(r['lat']), "long": float(r['long'])} for r in rows]
    return JsonResponse(data, safe=False)

@cache_page(60 * 60 * 24)
def stats_vehicle_types(request):
    """
    Regroupe les catégories de véhicules en 7 familles lisibles
    et retourne pour chaque groupe : le total et la liste des types
    inclus (pour l'affichage dans le tooltip côté React).
    Les libellés en base correspondent exactement aux valeurs de
    MAP_CATV dans import_csv.py.
    """

    GROUPS = {
        'Voiture légère': {
            'color': '#378ADD',
            'members': ['VL seul', 'Voiturette'],
        },
        'Deux/trois-roues motorisés': {
            'color': '#D85A30',
            'members': [
                'Cyclomoteur <50cm3',
                'Scooter < 50 cm3',
                'Motocyclette > 50 cm3 et <= 125 cm3',
                'Scooter > 50 cm3 et <= 125 cm3',
                'Motocyclette > 125 cm3',
                'Scooter > 125 cm3',
                '3RM <= 50 cm3',
                '3RM 50 cm3 <= 125 cm3',
                '3RM > 125 cm3',
            ],
        },
        'Véhicule utilitaire léger': {
            'color': '#0F6E56',
            'members': ['VU seul 1,5T <= PTAC <= 3,5T'],
        },
        'Poids lourds': {
            'color': '#1D9E75',
            'members': [
                'PL seul 3,5T <PTCA <= 7,5T',
                'PL seul > 7,5T',
                'PL > 3,5T + remorque',
                'Tracteur routier seul',
                'Tracteur routier + semi-remorque',
            ],
        },
        'Mobilité douce': {
            'color': '#BA7517',
            'members': ['Bicyclette', 'VAE', 'EDP à moteur', 'EDP sans moteur'],
        },
        'Transports en commun': {
            'color': '#7F77DD',
            'members': ['Autobus', 'Autocar', 'Train', 'Tramway'],
        },
        'Engins spéciaux / autres': {
            'color': '#888780',
            'members': [
                'Engin spécial',
                'Tracteur agricole',
                'Quad léger <= 50 cm3',
                'Quad lourd > 50 cm3',
                'Autre véhicule',
                'Indéterminable',
            ],
        },
    }

    # Comptage ORM groupé par catv — une seule requête SQL
    raw = (
        Vehicule.objects
        .values('catv')
        .annotate(total=Count('id_vehicule'))
    )
    counts = {row['catv']: row['total'] for row in raw}

    result = []
    for group_name, meta in GROUPS.items():
        total = sum(counts.get(m, 0) for m in meta['members'])
        present_members = [m for m in meta['members'] if counts.get(m, 0) > 0]
        result.append({
            'group':   group_name,
            'total':   total,
            'color':   meta['color'],
            'members': present_members,
        })

    result.sort(key=lambda x: x['total'], reverse=True)
    return JsonResponse(result, safe=False)

@cache_page(60 * 60 * 24)
def stats_holiday_periods(request):
    buckets = {"Hiver": 0, "Printemps": 0, "Été": 0, "Automne": 0}

    rows = (
        Accident.objects
        .exclude(mois__isnull=True)
        .exclude(mois='')
        .values('mois')
        .annotate(total=Count('Num_Acc'))
    )

    for row in rows:
        try:
            mois = int(row['mois'])
            if mois in [12, 1, 2]:
                buckets["Hiver"] += row['total']
            elif mois in [3, 4, 5]:
                buckets["Printemps"] += row['total']
            elif mois in [6, 7, 8]:
                buckets["Été"] += row['total']
            else:
                buckets["Automne"] += row['total']
        except (ValueError, TypeError):
            continue

    data = [{"periode": k, "total": v} for k, v in buckets.items()]
    return JsonResponse(data, safe=False)

@cache_page(60 * 60 * 24)
def stats_age_gravity(request):
    """
    Pour chaque tranche d'âge, retourne le nombre d'usagers par niveau de gravité.
    L'âge est calculé depuis l'année de l'accident (Num_Acc__an) et non
    une constante, pour coller aux données réelles du dataset.

    On utilise une annotation ORM (ExpressionWrapper + Cast) pour calculer
    l'âge côté base de données — pas de boucle Python sur des milliers de lignes.
    """

    AGE_RANGES = ['0-17', '18-25', '26-40', '41-65', '65+']
    VALID_GRAV = {'Tué', 'Blessé hospitalisé', 'Blessé léger', 'Indemne'}

    buckets = {
        r: {
            'age_range':          r,
            'Tué':                0,
            'Blessé hospitalisé': 0,
            'Blessé léger':       0,
            'Indemne':            0,
        }
        for r in AGE_RANGES
    }

    # Jointure Usager → Accident via Num_Acc pour récupérer l'année de l'accident,
    # puis calcul de l'âge = an_accident - an_nais entièrement côté DB
    rows = (
        Usager.objects
        .exclude(an_nais__isnull=True)
        .exclude(an_nais='')
        .exclude(grav__isnull=True)
        .filter(grav__in=VALID_GRAV)
        .annotate(
            age=ExpressionWrapper(
                Cast(F('Num_Acc__an'), IntegerField()) - Cast(F('an_nais'), IntegerField()),
                output_field=IntegerField()
            )
        )
        .values('age', 'grav')
    )

    for row in rows:
        try:
            age  = int(row['age'])
            grav = row['grav']

            if age < 0 or age > 120:   # filtre les années de naissance aberrantes
                continue

            if age <= 17:
                bucket_key = '0-17'
            elif age <= 25:
                bucket_key = '18-25'
            elif age <= 40:
                bucket_key = '26-40'
            elif age <= 65:
                bucket_key = '41-65'
            else:
                bucket_key = '65+'

            buckets[bucket_key][grav] += 1

        except (ValueError, TypeError):
            continue

    return JsonResponse(list(buckets.values()), safe=False)

@cache_page(60 * 60 * 24)
def stats_sex_gravity(request):
    """
    Pour chaque sexe, retourne le nombre d'usagers par niveau de gravité.
    Les valeurs en base sont déjà : 'Masculin', 'Féminin'
    pour sexe, et les libellés texte pour grav.
    """
    VALID_SEXE = {'Masculin', 'Féminin'}
    VALID_GRAV = {'Tué', 'Blessé hospitalisé', 'Blessé léger', 'Indemne'}

    buckets = {
        sexe: {'sexe': sexe, 'Tué': 0, 'Blessé hospitalisé': 0, 'Blessé léger': 0, 'Indemne': 0}
        for sexe in VALID_SEXE
    }

    rows = (
        Usager.objects
        .filter(sexe__in=VALID_SEXE, grav__in=VALID_GRAV)
        .values('sexe', 'grav')
        .annotate(total=Count('id_usager'))
    )

    for row in rows:
        buckets[row['sexe']][row['grav']] = row['total']

    return JsonResponse(list(buckets.values()), safe=False)


def _load_departments():
    if not os.path.exists(_DEPTS_PATH):
        resp = requests.get(_DEPTS_URL, timeout=20)
        resp.raise_for_status()
        with open(_DEPTS_PATH, 'w', encoding='utf-8') as f:
            f.write(resp.text)
    with open(_DEPTS_PATH, encoding='utf-8') as f:
        return json.load(f)


def _get_departments_indexed():
    """Charge les départements une seule fois et construit un STRtree pour filtrage rapide."""
    global _departments, _departments_idx
    if _departments is None:
        geojson = _load_departments()
        _departments = [
            (
                feat['properties'].get('code', ''),
                feat['properties'].get('nom',  ''),
                shape(feat['geometry']),
            )
            for feat in geojson['features']
        ]
        _departments_idx = STRtree([geom for _, _, geom in _departments])
    return _departments, _departments_idx


_CLUSTERING_MODELS = {'kmeans', 'bisecting_kmeans', 'gmm'}
_N_CLUSTERS        = 5
# Mapping clé frontend → model_name stocké dans ClusterDepartement
_CD_MODEL_MAP      = {'kmeans': 'kmeans', 'bisecting_kmeans': 'bisecting', 'gmm': 'gmm'}

# Seuils basés sur le score de gravité pondéré (pct_tue×5 + pct_grave×3 + pct_leger×2)
_NIVEAU_SEUILS      = [(210, 'élevé'), (186, 'modéré')]  # calibrés sur P66/P33 des pires clusters
_SEUIL_MOYEN_FAIBLE = 130                               # ≈ P25 de la distribution nationale des scores moyens

_CONSEIL_CONDITION = [
    ('Nuit sans éclairage', "Les accidents nocturnes sans éclairage sont parmi les plus mortels. Évitez de conduire de nuit sur ces tronçons ou réduisez significativement votre vitesse."),
    ('Nuit éclairée',       "La conduite de nuit reste plus dangereuse même sur routes éclairées. Soyez attentif aux piétons et cycles."),
    ('Autoroute',           "Sur les portions autoroutières à vitesse élevée, maintenez impérativement vos distances de sécurité et faites une pause toutes les 2 heures."),
    ('Hors agglo',          "Les routes hors agglomération concentrent les accidents les plus graves. Respectez strictement les limitations et anticipez les croisements."),
    ('Route dép.',          "Les routes départementales présentent de nombreux risques aux intersections et virages. Adaptez votre allure et ne dépassez pas sans visibilité suffisante."),
    ('Route nat.',          "Les routes nationales à trafic mixte requièrent une vigilance constante, notamment lors des dépassements."),
]

_CONSEIL_NIVEAU = {
    'faible':  "Ce trajet présente un faible niveau de risque d'accident grave.",
    'modéré':  "Ce trajet traverse des zones à risque modéré : une vigilance accrue est recommandée.",
    'élevé':   "Attention : ce trajet inclut des zones à risque élevé de blessures graves ou mortelles.",
}


def _generate_recommendation(ordered, risk_profiles):
    """Génère une recommandation globale pour le trajet à partir des profils de risque."""
    dept_data = []
    for dept in ordered:
        clusters = risk_profiles.get(dept['code'], [])
        if not clusters:
            continue
        worst     = clusters[-1]
        avg_score = sum(c['gravity_score'] for c in clusters) / len(clusters)
        dept_data.append({
            'nom':       dept['nom'],
            'score':     worst['gravity_score'],  # pire cluster — pour le niveau de la bannière
            'avg_score': avg_score,               # moyenne — pour l'alerte et le comptage faible
            'pct_tue':   worst['pct_tue'],
            'profil':    worst.get('profil', ''),
        })

    if not dept_data:
        return None

    max_score = max(d['score'] for d in dept_data)
    niveau = 'faible'
    for seuil, label in _NIVEAU_SEUILS:
        if max_score >= seuil:
            niveau = label
            break

    # Alerte et faible utilisent avg_score → cohérents, pas de contradiction possible
    top = sorted(dept_data, key=lambda x: x['avg_score'], reverse=True)[:2]

    alerte_parts = [d['nom'] for d in top if d['pct_tue'] > 0.5]
    alerte = (
        f"Vigilance accrue en {' et '.join(alerte_parts)}."
        if alerte_parts else
        f"Département le plus exposé : {top[0]['nom']}."
    )

    # Conseil contextuel basé sur la condition dominante du pire département
    profil_pire = top[0]['profil'] or ''
    conseil_condition = next(
        (texte for mot, texte in _CONSEIL_CONDITION if mot in profil_pire),
        "Adoptez une conduite prudente et anticipez les aléas tout au long du trajet."
    )
    conseil = f"{_CONSEIL_NIVEAU[niveau]} {conseil_condition}"

    nb_safe = sum(1 for d in dept_data if d['avg_score'] < _SEUIL_MOYEN_FAIBLE)
    nb_total = len(dept_data)
    if nb_safe == nb_total:
        bilan_positif = f"L'ensemble des {nb_total} départements traversés présente un profil de risque faible."
    elif nb_safe > 0:
        bilan_positif = f"{nb_safe} département{'s' if nb_safe > 1 else ''} sur {nb_total} présente{'nt' if nb_safe > 1 else ''} un profil de risque faible."
    else:
        bilan_positif = None

    # Recommandation horaire si la condition dominante est nocturne
    _MOTS_NUIT = ['Nuit sans éclairage', 'Nuit éclairée', 'Nuit non éclairée', 'Crépuscule']
    if any(m in profil_pire for m in _MOTS_NUIT):
        horaire = "Privilégiez un départ entre 7h et 19h pour éviter les tronçons à risque nocturne."
    else:
        horaire = None

    return {
        'niveau':              niveau,
        'alerte':              alerte,
        'conseil':             conseil,
        'bilan_positif':       bilan_positif,
        'horaire':             horaire,
        'condition_dominante': profil_pire,
    }


def get_departments_list(request):
    depts, _ = _get_departments_indexed()
    data = sorted(
        [{'code': code, 'nom': nom} for code, nom, _ in depts],
        key=lambda x: x['nom'],
    )
    return JsonResponse(data, safe=False)


def get_simulator_prediction(request):
    dep  = request.GET.get('dep',  '').strip()
    lum  = request.GET.get('lum',  '').strip()
    atm  = request.GET.get('atm',  '').strip()
    agg  = request.GET.get('agg',  '').strip()
    catr = request.GET.get('catr', '').strip()
    catv = request.GET.get('catv', '').strip()
    vma  = request.GET.get('vma',  '').strip()

    if not all([dep, lum, atm, agg, catr, vma]):
        return JsonResponse({'error': 'Tous les paramètres sont requis.'}, status=400)

    try:
        bundle = _load_sim_model('simulator_model')
        pre    = bundle['preprocesseur']
        model  = bundle['model']
    except Exception as e:
        return JsonResponse({'error': f'Modèle simulateur non disponible : {e}'}, status=500)

    try:
        vma_val = float(vma)
        if vma_val <= 0:
            vma_val = np.nan
    except ValueError:
        vma_val = np.nan

    X_new = pd.DataFrame([{
        'lum': lum, 'atm': atm, 'agg': agg,
        'catr': catr, 'catv': catv or 'VL seul',
        'dep': dep, 'vma': vma_val,
    }])

    try:
        X_t    = pre.transform(X_new)
        probas = model.predict_proba(X_t)[0]
    except Exception as e:
        return JsonResponse({'error': f'Erreur de prédiction : {e}'}, status=500)

    GRAV_FIELD = {
        'Indemne':            'pct_indemne',
        'Blessé léger':       'pct_blesse_leger',
        'Blessé hospitalisé': 'pct_blesse_grave',
        'Tué':                'pct_tue',
    }
    result = {'pct_indemne': 0.0, 'pct_blesse_leger': 0.0, 'pct_blesse_grave': 0.0, 'pct_tue': 0.0}
    for cls, p in zip(model.classes_, probas):
        field = GRAV_FIELD.get(cls)
        if field:
            result[field] = round(float(p) * 100, 2)

    result['methode'] = 'Random Forest calibré (CalibratedClassifierCV)'
    return JsonResponse(result)


@cache_page(60 * 60 * 6)
def get_route_departments(request):
    depart      = request.GET.get('depart',  '').strip()
    arrivee     = request.GET.get('arrivee', '').strip()
    model_name  = request.GET.get('model', 'kmeans')

    if not depart or not arrivee:
        return JsonResponse({'error': 'Les paramètres depart et arrivee sont requis.'}, status=400)

    if model_name not in _CLUSTERING_MODELS:
        return JsonResponse({'error': f'Modèle inconnu : {model_name}'}, status=400)

    def geocode(city):
        # Nominatim en priorité
        try:
            resp = requests.get(
                'https://nominatim.openstreetmap.org/search',
                params={'q': f'{city}, France', 'format': 'json', 'limit': 1, 'countrycodes': 'fr'},
                headers={'User-Agent': 'PSID-AccidentsRoutiers/1.0'},
                timeout=8,
            )
            data = resp.json()
            if data:
                return float(data[0]['lon']), float(data[0]['lat']), data[0].get('display_name', city)
        except Exception:
            pass

        # Fallback : API Adresse officielle (data.gouv.fr) — sans rate-limit
        try:
            resp = requests.get(
                'https://api-adresse.data.gouv.fr/search/',
                params={'q': city, 'limit': 1, 'type': 'municipality'},
                timeout=10,
            )
            features = resp.json().get('features', [])
            if features:
                coords = features[0]['geometry']['coordinates']  # [lon, lat]
                label  = features[0]['properties'].get('label', city)
                return float(coords[0]), float(coords[1]), label
        except Exception:
            pass

        return None

    geo_dep = geocode(depart)
    geo_arr = geocode(arrivee)

    if not geo_dep:
        return JsonResponse({'error': f'Ville introuvable : {depart}'}, status=404)
    if not geo_arr:
        return JsonResponse({'error': f'Ville introuvable : {arrivee}'}, status=404)

    lon1, lat1, label_dep = geo_dep
    lon2, lat2, label_arr = geo_arr

    try:
        osrm_resp = requests.get(
            f'http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}'
            '?overview=full&geometries=geojson',
            timeout=30,
        )
        osrm_data = osrm_resp.json()
    except Exception as e:
        return JsonResponse({'error': f'Erreur serveur de routage : {e}'}, status=502)

    if osrm_data.get('code') != 'Ok' or not osrm_data.get('routes'):
        return JsonResponse({'error': 'Impossible de calculer cet itinéraire.'}, status=500)

    try:
        route      = osrm_data['routes'][0]
        coords     = route['geometry']['coordinates']   # [[lon, lat], ...]
        dist_km    = round(route['distance'] / 1000, 1)
        dur_min    = round(route['duration'] / 60)
        route_line = LineString([(c[0], c[1]) for c in coords])

        departments, dept_tree = _get_departments_indexed()

        # STRtree : filtre d'abord les candidats par bounding-box, puis vérifie l'intersection réelle
        candidate_idxs = dept_tree.query(route_line, predicate='intersects')

        dept_first_pos = {}
        for idx in candidate_idxs:
            code, nom, geom = departments[idx]
            first = next(
                (i for i, c in enumerate(coords) if geom.contains(Point(c[0], c[1]))),
                len(coords),
            )
            dept_first_pos[code] = (first, nom)

        ordered = [
            {'code': code, 'nom': nom}
            for code, (_pos, nom) in sorted(dept_first_pos.items(), key=lambda x: x[1][0])
        ]

        dept_codes  = [d['code'] for d in ordered]
        col_map     = {'kmeans': 'cluster_kmeans', 'bisecting_kmeans': 'cluster_bisecting', 'gmm': 'cluster_gmm'}
        cluster_col = col_map[model_name]

        df_lab = _get_labelled_df()
        df_dep = df_lab[df_lab['dep'].isin(dept_codes)] if not df_lab.empty else df_lab
        acc_to_cluster = dict(zip(df_dep['Num_Acc'], df_dep[cluster_col])) if not df_dep.empty else {}

        cd_model = _CD_MODEL_MAP.get(model_name, 'kmeans')
        profiles = ClusterDepartement.objects.filter(
            model_name=cd_model, departement__in=dept_codes
        ).values('departement', 'cluster_number', 'pct_indemne', 'pct_blesse_leger', 'pct_blesse_grave', 'pct_tue', 'recommandation')

        risk_profiles = {}
        for p in profiles:
            entry = {
                'cluster_number':   p['cluster_number'],
                'pct_indemne':      p['pct_indemne'],
                'pct_blesse_leger': p['pct_blesse_leger'],
                'pct_blesse_grave': p['pct_blesse_grave'],
                'pct_tue':          p['pct_tue'],
                'gravity_score':    round(
                    p['pct_tue'] * 5 + p['pct_blesse_grave'] * 3 + p['pct_blesse_leger'], 1
                ),
                'profil': p['recommandation'] or '',
            }
            risk_profiles.setdefault(p['departement'], []).append(entry)

        for dep in risk_profiles:
            risk_profiles[dep].sort(key=lambda x: x['gravity_score'])

        journey_rec = _generate_recommendation(ordered, risk_profiles)

        gravity_rank_map = {
            dep: {c['cluster_number']: idx for idx, c in enumerate(clusters)}
            for dep, clusters in risk_profiles.items()
        }

        acc_qs = (
            Accident.objects
            .filter(dep__in=dept_codes, lat__isnull=False, long__isnull=False)
            .exclude(lat=0, long=0)
            .values('Num_Acc', 'lat', 'long', 'dep')[:2000]
        )
        cluster_points = []
        for acc in acc_qs:
            cnum = acc_to_cluster.get(acc['Num_Acc'])
            if cnum is None:
                continue
            rank = gravity_rank_map.get(acc['dep'], {}).get(int(cnum), 0)
            cluster_points.append({'lat': float(acc['lat']), 'lon': float(acc['long']), 'rank': rank})

        return JsonResponse({
            'depart':                 {'label': label_dep, 'lon': lon1, 'lat': lat1},
            'arrivee':                {'label': label_arr, 'lon': lon2, 'lat': lat2},
            'distance_km':            dist_km,
            'duration_min':           dur_min,
            'departements':           ordered,
            'route':                  coords,
            'cluster_points':         cluster_points,
            'total_accidents':        len(df_dep),
            'model':                  model_name,
            'risk_profiles':          risk_profiles,
            'journey_recommendation': journey_rec,
        })

    except Exception as e:
        return JsonResponse({'error': f'Erreur interne : {e}'}, status=500)
