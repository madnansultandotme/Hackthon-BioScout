from django.urls import path, include
from . import web_urls

urlpatterns = [
    # Web URLs
    *web_urls.urlpatterns,
] 