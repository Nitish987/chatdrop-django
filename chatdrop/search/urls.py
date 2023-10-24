from django.urls import path
from . import views

urlpatterns = [
    path('v1/search/profiles/', views.SearchProfiles.as_view(), name='search-profiles'),
    path('v1/search/audios/', views.SearchAudios.as_view(), name='search-audios'),
]
