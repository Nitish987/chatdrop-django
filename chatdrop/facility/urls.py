from django.urls import path
from . import views


urlpatterns = [
    path('v1/linkpreview/', views.LinkPreview.as_view(), name='link-preview-v1'),
]