from django.urls import path
from . import views

urlpatterns = [
    path('accidents/locations/', views.get_all_locations, name='accident_locations'),
    path('accident/<int:num_acc>/', views.get_accident_details, name='accident_details'),

    path('stats/sex-gravity/', views.stats_sex_gravity),
    path('stats/age-gravity/', views.stats_age_gravity),
    
    path('stats/vehicle-types/', views.stats_vehicle_types),
    path('stats/holiday-periods/', views.stats_holiday_periods),

]