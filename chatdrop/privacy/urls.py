from django.urls import path
from . import views

urlpatterns = [
    path('v1/block/', views.BlockUser.as_view(), name='block-user'),
    path('v1/report/', views.ReportUser.as_view(), name='report-user'),
]