from django.http import JsonResponse
from .models import Accident, Vehicule, Usager
from django.forms.models import model_to_dict # 1. On importe cet outil magique
from django.db.models import ExpressionWrapper, IntegerField, F
from django.db.models.functions import Cast
from django.views.decorators.cache import cache_page

from django.db.models import Count

def get_accident_details(request, num_acc):
    try:
        # 1. On cherche l'accident principal grâce au Num_Acc
        accident = Accident.objects.get(Num_Acc=num_acc)
        
        # 2. On aspire TOUTES les colonnes de l'accident en une seule ligne
        caract_data = model_to_dict(accident)
        
        # 3. Petit bonus : on ajoute une vraie date formatée pour faciliter le travail de React plus tard
        caract_data['date_formatee'] = f"{accident.jour}/{accident.mois}/{accident.an}"

        data = {
            "caracteristiques": caract_data,
            "lieux": list(accident.lieux.values()),
            "vehicules": list(accident.vehicules.values()),
            "usagers": list(accident.usagers.values())
        }
        
        # 4. On renvoie le tout au format JSON
        return JsonResponse(data)
        
    except Accident.DoesNotExist:
        # Sécurité : si le Num_Acc n'existe pas en base
        return JsonResponse({"erreur": "Cet accident n'existe pas dans la base de données."}, status=404)

@cache_page(60 * 60 * 24)
def get_all_locations(request):
    """
    Renvoie uniquement les coordonnées pour alléger le chargement de la carte.
    """
    rows = (
        Accident.objects
        .filter(lat__isnull=False, long__isnull=False)
        .values('Num_Acc', 'lat', 'long')[:100]
    )
    data = [{"id": r['Num_Acc'], "lat": float(r['lat']), "long": float(r['long'])} for r in rows]
    return JsonResponse(data, safe=False)

# Graphiques :

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
    # Index rapide : libellé → count
    counts = {row['catv']: row['total'] for row in raw}

    result = []
    for group_name, meta in GROUPS.items():
        total = sum(counts.get(m, 0) for m in meta['members'])
        # On n'inclut que les membres réellement présents en base dans la liste du tooltip
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
