from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('casualty/<str:soldier_id>/', views.casualty_card_view, name='casualty_card'),
    path('hospital/', views.hospital_standby_view, name='hospital_view'),
    path('map/', views.map_view, name='map_view'),
    path('api/soldiers/', views.api_soldiers_view, name='api_soldiers'),
    path('api/health/', views.api_health_view, name='api_health'),
    path('api/medical/confirm/', views.api_confirm_medical_view, name='api_confirm_medical'),
    path('api/medical/clear/<str:soldier_id>/', views.api_clear_medical_view, name='api_clear_medical'),
    path('api/medical/<str:soldier_id>/', views.api_medical_entries_view, name='api_medical_entries'),
    path('api/medical/', views.api_add_medical_entry_view, name='api_add_medical_entry'),
]
