from django.urls import path
from . import web_views

urlpatterns = [
    path('v2/notifications/', web_views.UserNotificationsV2.as_view(), name='web-notifications-v2'),
    path('v1/notification/read/', web_views.ReadNotifications.as_view(), name='web-notification-read'),
]