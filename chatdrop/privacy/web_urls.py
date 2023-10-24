from django.urls import path
from . import web_views

urlpatterns = [
    path('v1/block/', web_views.BlockUser.as_view(), name='web-block-user'),
    path('v1/report/', web_views.ReportUser.as_view(), name='web-report-user'),
]