from django.urls import path
from . import views
from .views import rag_qa_view, rag_qa_ajax, home

urlpatterns = [
    path('', home, name='home'),
    path('submit/', views.ObservationCreateView.as_view(), name='submit_observation'),
    path('<int:pk>/', views.ObservationDetailView.as_view(), name='observation_detail'),
    path('<int:pk>/edit/', views.ObservationUpdateView.as_view(), name='observation_edit'),
    path('<int:pk>/delete/', views.ObservationDeleteView.as_view(), name='observation_delete'),
    path('<int:pk>/validate/', views.validate_observation, name='validate_observation'),
    path('<int:pk>/correction/', views.submit_correction_request, name='submit_correction_request'),
    path('<int:pk>/correction/<int:req_id>/<str:action>/', views.review_correction_request, name='review_correction_request'),
    path('rag-qa/', rag_qa_view, name='rag_qa'),
    path('rag-qa/ajax/', rag_qa_ajax, name='rag_qa_ajax'),
    path('observations/', views.ObservationListView.as_view(), name='observation_list'),
] 