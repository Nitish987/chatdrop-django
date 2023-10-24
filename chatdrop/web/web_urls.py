from django.urls import path
from . import web_views

urlpatterns = [
    path('token/csrf/', web_views.AttachCsrf.as_view(), name='web-csrf-attach')
]