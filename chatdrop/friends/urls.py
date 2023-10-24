from django.urls import path
from . import views

urlpatterns = [
    path('v1/friend/request/send/', views.SendFriendRequest.as_view(), name='send-friend-request'),
    path('v1/friend/request/<str:request_id>/accept/', views.AcceptFriendRequest.as_view(), name='accept-friend-request'),
    path('v1/unfriend/', views.UnFriend.as_view(), name='unfriend'),
    path('v1/friend/list/', views.ListFriend.as_view(), name='friend-list'),
    path('v1/friend/check/', views.IsFriend.as_view(), name='is-friend'),
    path('v1/friend/request/list/', views.ListFriendRequest.as_view(), name='friend-request-list'),
]
