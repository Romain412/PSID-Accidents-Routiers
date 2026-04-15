from django.urls import path
from . import views

urlpatterns = [
    # Nouvelle route pour la carte (attention à l'ordre, mets-la en haut)
    path('accidents/locations/', views.get_all_locations, name='accident_locations'),
    # Attention, on ne remet pas "api/" ici car core/urls.py s'en est déjà chargé !
    path('accident/<int:num_acc>/', views.get_accident_details, name='accident_details'),
    
]