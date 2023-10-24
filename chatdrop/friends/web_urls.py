from django.urls import path
from . import web_views

urlpatterns = [
    path('v1/friend/request/send/', web_views.SendFriendRequest.as_view(), name='web-send-friend-request'),
    path('v1/friend/request/<str:request_id>/accept/', web_views.AcceptFriendRequest.as_view(), name='web-accept-friend-request'),
    path('v1/unfriend/', web_views.UnFriend.as_view(), name='web-unfriend'),
    path('v1/friend/list/', web_views.ListFriend.as_view(), name='web-friend-list'),
    path('v1/friend/check/', web_views.IsFriend.as_view(), name='web-is-friend'),
    path('v1/friend/request/list/', web_views.ListFriendRequest.as_view(), name='web-friend-request-list'),
]
