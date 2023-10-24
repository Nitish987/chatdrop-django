from django.urls import path
from . import views

urlpatterns = [
    path('v1/notifications/', views.UserNotifications.as_view(), name='notifications'), # deprecated
    path('v2/notifications/', views.UserNotificationsV2.as_view(), name='notifications-v2'),
    
    path('v1/notification/read/', views.ReadNotifications.as_view(), name='notification-read'),
]