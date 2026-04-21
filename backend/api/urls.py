from django.urls import path
from . import views

urlpatterns = [
    # Nouvelle route pour la carte (attention à l'ordre, mets-la en haut)
    path('accidents/locations/', views.get_all_locations, name='accident_locations'),
    # Attention, on ne remet pas "api/" ici car core/urls.py s'en est déjà chargé !
    path('accident/<int:num_acc>/', views.get_accident_details, name='accident_details'),
    path('accidents/locations/', views.get_all_locations),

    path('stats/gravity-distribution/', views.stats_gravity_distribution),
    path('stats/sex-gravity/', views.stats_sex_gravity),
    
    path('stats/vehicle-types/', views.stats_vehicle_types),
    path('stats/road-types/', views.stats_road_types),
    path('stats/holiday-periods/', views.stats_holiday_periods),

    path('stats/age-gravity/', views.stats_age_gravity),


]