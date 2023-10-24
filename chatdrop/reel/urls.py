from django.urls import path
from . import views


urlpatterns = [
    path('v1/reel/add/', views.AddReel.as_view(), name='add-reel'),
    path('v1/reel/<str:reel_id>/view/', views.SingleReelView.as_view(), name='single-reel-view'),
    path('v1/reel/<str:reel_id>/viewer/', views.ReelViewer.as_view(), name='reel-viewer'),
    path('v1/reel/<str:reel_id>/visibility/', views.ChangeReelVisilibity.as_view(), name='add-reel-visibility'),
    path('v1/reel/list/', views.ListReel.as_view(), name='list-reel'),
    path('v1/reel/<str:reel_id>/delete/', views.DeleteReel.as_view(), name='delete-reel'),
    path('v1/reel/<str:reel_id>/comment/', views.Comment.as_view(), name='add-and-list-reel-comment'),
    path('v1/reel/<str:reel_id>/comment/<str:comment_id>/delete/', views.DeleteComment.as_view(), name='delete-reel-comment'),
    path('v1/reel/<str:reel_id>/like/', views.Like.as_view(), name='reel-like'),
    path('v1/reel/comment/<str:comment_id>/like/', views.CommentLike.as_view(), name='reel-comment-like'),
    path('v1/audio/add/', views.AddAudio.as_view(), name='add-audio'),
    path('v1/audio/list/', views.ListAudio.as_view(), name='list-audio'),
    path('v1/audio/<int:audio_id>/delete/', views.DeleteAudio.as_view(), name='delete-audio'),
]