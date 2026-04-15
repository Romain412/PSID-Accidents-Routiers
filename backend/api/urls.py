from django.urls import path
from . import views

urlpatterns = [
    # Attention, on ne remet pas "api/" ici car core/urls.py s'en est déjà chargé !
    path('accident/<int:num_acc>/', views.get_accident_details, name='accident_details'),
]