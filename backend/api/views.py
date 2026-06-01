from django.http import JsonResponse
from .models import Accident, Vehicule, Usager
from django.forms.models import model_to_dict
from django.db.models import ExpressionWrapper, IntegerField, F
from django.db.models.functions import Cast
from django.views.decorators.cache import cache_page
from django.db.models import Count

import json
import os
import requests
import numpy as np
from shapely.geometry import shape, LineString, Point
from sklearn.cluster import KMeans, BisectingKMeans
from sklearn.mixture import GaussianMixture

_DEPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'departements.geojson')
_DEPTS_URL = (
    'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/'
    'departements-version-simplifiee.geojson'
)

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
        .values('Num_Acc', 'lat', 'long')[:1000]
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


_CLUSTERING_MODELS = {'kmeans', 'bisecting_kmeans', 'gmm'}
_N_CLUSTERS        = 5

def get_route_departments(request):
    depart      = request.GET.get('depart',  '').strip()
    arrivee     = request.GET.get('arrivee', '').strip()
    model_name  = request.GET.get('model', 'kmeans')

    if not depart or not arrivee:
        return JsonResponse({'error': 'Les paramètres depart et arrivee sont requis.'}, status=400)

    if model_name not in _CLUSTERING_MODELS:
        return JsonResponse({'error': f'Modèle inconnu : {model_name}'}, status=400)

    def geocode(city):
        resp = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': f'{city}, France', 'format': 'json', 'limit': 1, 'countrycodes': 'fr'},
            headers={'User-Agent': 'PSID-AccidentsRoutiers/1.0'},
            timeout=10,
        )
        data = resp.json()
        if not data:
            return None
        return float(data[0]['lon']), float(data[0]['lat']), data[0].get('display_name', city)

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

    route      = osrm_data['routes'][0]
    coords     = route['geometry']['coordinates']   # [[lon, lat], ...]
    dist_km    = round(route['distance'] / 1000, 1)
    dur_min    = round(route['duration'] / 60)
    route_line = LineString([(c[0], c[1]) for c in coords])

    try:
        geojson = _load_departments()
    except Exception as e:
        return JsonResponse({'error': f'Erreur chargement départements : {e}'}, status=500)

    departments = [
        (
            feat['properties'].get('code', ''),
            feat['properties'].get('nom',  ''),
            shape(feat['geometry']),
        )
        for feat in geojson['features']
    ]

    dept_first_pos = {}
    for code, nom, geom in departments:
        if not geom.intersects(route_line):
            continue
        for i, c in enumerate(coords):
            if geom.intersects(Point(c[0], c[1])):
                dept_first_pos[code] = (i, nom)
                break
        else:
            dept_first_pos[code] = (len(coords), nom)

    ordered = [
        {'code': code, 'nom': nom}
        for code, (_pos, nom) in sorted(dept_first_pos.items(), key=lambda x: x[1][0])
    ]

    # ── Clustering des accidents dans les départements traversés ──────────────
    dept_codes = [d['code'] for d in ordered]
    acc_rows = (
        Accident.objects
        .filter(dep__in=dept_codes, lat__isnull=False, long__isnull=False)
        .exclude(lat=0, long=0)
        .values('lat', 'long')[:2000]
    )
    points = np.array([[float(a['lat']), float(a['long'])] for a in acc_rows])

    clusters_list = []
    if len(points) >= _N_CLUSTERS:
        k = min(_N_CLUSTERS, len(points))
        if model_name == 'kmeans':
            labels = KMeans(n_clusters=k, random_state=42, n_init='auto').fit_predict(points)
        elif model_name == 'bisecting_kmeans':
            labels = BisectingKMeans(n_clusters=k, random_state=42).fit_predict(points)
        else:
            gm = GaussianMixture(n_components=k, random_state=42)
            gm.fit(points)
            labels = gm.predict(points)

        cluster_map = {}
        for point, label in zip(points, labels):
            cluster_map.setdefault(int(label), []).append([float(point[0]), float(point[1])])

        clusters_list = [
            {'id': cid, 'count': len(pts), 'points': pts}
            for cid, pts in sorted(cluster_map.items())
        ]

    return JsonResponse({
        'depart':           {'label': label_dep, 'lon': lon1, 'lat': lat1},
        'arrivee':          {'label': label_arr, 'lon': lon2, 'lat': lat2},
        'distance_km':      dist_km,
        'duration_min':     dur_min,
        'departements':     ordered,
        'route':            coords,
        'clusters':         clusters_list,
        'total_accidents':  len(points),
        'model':            model_name,
    })
