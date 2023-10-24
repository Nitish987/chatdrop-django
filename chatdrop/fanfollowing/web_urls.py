from django.urls import path
from . import web_views

urlpatterns = [
    path('v1/follow/request/send/', web_views.SendFollowRequest.as_view(), name='web-send-follow-request'),
    path('v1/follow/request/<str:request_id>/accept/', web_views.AcceptFollowRequest.as_view(), name='web-accept-follow-request'),
    path('v1/unfollow/', web_views.Unfollow.as_view(), name='web-unfollow'),
    path('v1/unfollow/force/', web_views.ForceUnfollow.as_view(), name='web-force-unfollow'),
    path('v1/followers/list/', web_views.ListFollowers.as_view(), name='web-followers'),
    path('v1/followings/list/', web_views.ListFollowings.as_view(), name='web-followings'),
]
