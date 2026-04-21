from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .models import Accident, Vehicule, Lieu, Usager
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

@cache_page(60 * 15)
def get_all_locations(request):
    """
    Renvoie uniquement les coordonnées pour alléger le chargement de la carte.
    """
    # On récupère les accidents qui ont bien une latitude et une longitude
    accidents = Accident.objects.filter(lat__isnull=False, long__isnull=False)
    accidents = accidents[:100] #pour l'instant on limite le nb d'accidents pour de meilleures performances
    
    data = []
    for acc in accidents:
        # On s'assure de convertir les Decimal en float pour le JSON
        data.append({
            "id": acc.Num_Acc,
            "lat": float(acc.lat),
            "long": float(acc.long)
        })
        
    return JsonResponse(data, safe=False)

# Graphiques :

def stats_rain_correlation(request):
    data = (
        Accident.objects
        .values('atm')
        .annotate(total=Count('Num_Acc'))
        .order_by('-total')
    )

    return JsonResponse(list(data), safe=False)

def stats_vehicle_types(request):
    data = (
        Vehicule.objects
        .values('catv')
        .annotate(total=Count('id_vehicule'))
        .order_by('-total')
    )

    return JsonResponse(list(data), safe=False)

def stats_age_distribution(request):
    current_year = 2024

    usagers = Usager.objects.exclude(an_nais__isnull=True).exclude(an_nais='')

    buckets = {
        "0-17": 0,
        "18-25": 0,
        "26-40": 0,
        "41-65": 0,
        "65+": 0
    }

    for u in usagers:
        try:
            age = current_year - int(u.an_nais)

            if age <= 17:
                buckets["0-17"] += 1
            elif age <= 25:
                buckets["18-25"] += 1
            elif age <= 40:
                buckets["26-40"] += 1
            elif age <= 65:
                buckets["41-65"] += 1
            else:
                buckets["65+"] += 1

        except:
            continue

    data = [{"age_range": k, "total": v} for k, v in buckets.items()]
    return JsonResponse(data, safe=False)

def stats_road_types(request):
    data = (
        Lieu.objects
        .values('catr')
        .annotate(total=Count('Num_Acc'))
        .order_by('-total')
    )

    return JsonResponse(list(data), safe=False)

def stats_holiday_periods(request):
    buckets = {
        "Hiver": 0,
        "Printemps": 0,
        "Été": 0,
        "Automne": 0
    }

    accidents = Accident.objects.exclude(mois__isnull=True)

    for acc in accidents:
        try:
            mois = int(acc.mois)

            if mois in [12,1,2]:
                buckets["Hiver"] += 1
            elif mois in [3,4,5]:
                buckets["Printemps"] += 1
            elif mois in [6,7,8]:
                buckets["Été"] += 1
            else:
                buckets["Automne"] += 1

        except:
            continue

    data = [{"periode": k, "total": v} for k,v in buckets.items()]
    return JsonResponse(data, safe=False)

def stats_gravity_distribution(request):
    """
    Compte le nombre d'usagers par niveau de gravité.
    Les valeurs en base sont déjà : 'Indemne', 'Tué',
    'Blessé hospitalisé', 'Blessé léger'
    """
    data = (
        Usager.objects
        .values('grav')
        .annotate(total=Count('id_usager'))
        .order_by('grav')
    )
    return JsonResponse(list(data), safe=False)

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


def stats_sex_gravity(request):
    """
    Pour chaque sexe, retourne le nombre d'usagers par niveau de gravité.
    Les valeurs en base sont déjà : 'Masculin', 'Féminin'
    pour sexe, et les libellés texte pour grav.
    """
    VALID_SEXE = {'Masculin', 'Féminin'}
    VALID_GRAV = {'Tué', 'Blessé hospitalisé', 'Blessé léger', 'Indemne'}

    buckets = {
        sexe: {
            'sexe':               sexe,
            'Tué':                0,
            'Blessé hospitalisé': 0,
            'Blessé léger':       0,
            'Indemne':            0,
        }
        for sexe in VALID_SEXE
    }

    usagers = Usager.objects.exclude(sexe__isnull=True)

    for u in usagers:
        try:
            if u.sexe not in VALID_SEXE or u.grav not in VALID_GRAV:
                continue
            buckets[u.sexe][u.grav] += 1
        except (ValueError, TypeError):
            continue

    return JsonResponse(list(buckets.values()), safe=False)
