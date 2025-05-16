from django.urls import path
from .views import ObservationListCreateAPI, ObservationDetailAPI

urlpatterns = [
    path('', ObservationListCreateAPI.as_view(), name='observation_api'),
    path('<int:pk>/', ObservationDetailAPI.as_view(), name='observation_detail_api'),
] 