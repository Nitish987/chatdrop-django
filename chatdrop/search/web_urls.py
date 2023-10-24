from django.urls import path
from . import web_views

urlpatterns = [
    path('v1/search/profiles/', web_views.SearchProfiles.as_view(), name='web-search-profiles'),
    path('v1/search/audios/', web_views.SearchAudios.as_view(), name='web-search-audios'),
]
