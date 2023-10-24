from django.urls import path
from . import web_views


urlpatterns = [
    path('v1/linkpreview/', web_views.LinkPreview.as_view(), name='web-link-preview-v1'),
]