from django.urls import path
from . import views

urlpatterns = [
    path('v1/follow/request/send/', views.SendFollowRequest.as_view(), name='send-follow-request'),
    path('v1/follow/request/<str:request_id>/accept/', views.AcceptFollowRequest.as_view(), name='accept-follow-request'),
    path('v1/unfollow/', views.Unfollow.as_view(), name='unfollow'),
    path('v1/unfollow/force/', views.ForceUnfollow.as_view(), name='force-unfollow'),
    path('v1/followers/list/', views.ListFollowers.as_view(), name='followers'),
    path('v1/followings/list/', views.ListFollowings.as_view(), name='followings'),
]
