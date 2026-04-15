from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .models import Accident
from django.forms.models import model_to_dict # 1. On importe cet outil magique

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