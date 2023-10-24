from django.urls import path
from . import web_views


urlpatterns = [
    path('v1/reel/add/', web_views.AddReel.as_view(), name='web-add-reel'),
    path('v1/reel/<str:reel_id>/view/', web_views.SingleReelView.as_view(), name='web-single-reel-view'),
    path('v1/reel/<str:reel_id>/viewer/', web_views.ReelViewer.as_view(), name='web-reel-viewer'),
    path('v1/reel/<str:reel_id>/visibility/', web_views.ChangeReelVisilibity.as_view(), name='web-add-reel-visibility'),
    path('v1/reel/list/', web_views.ListReel.as_view(), name='web-list-reel'),
    path('v1/reel/<str:reel_id>/delete/', web_views.DeleteReel.as_view(), name='web-delete-reel'),
    path('v1/reel/<str:reel_id>/comment/', web_views.Comment.as_view(), name='web-add-and-list-reel-comment'),
    path('v1/reel/<str:reel_id>/comment/<str:comment_id>/delete/', web_views.DeleteComment.as_view(), name='web-delete-reel-comment'),
    path('v1/reel/<str:reel_id>/like/', web_views.Like.as_view(), name='web-reel-like'),
    path('v1/reel/comment/<str:comment_id>/like/', web_views.CommentLike.as_view(), name='web-reel-comment-like'),
    path('v1/audio/add/', web_views.AddAudio.as_view(), name='web-add-audio'),
    path('v1/audio/list/', web_views.ListAudio.as_view(), name='web-list-audio'),
    path('v1/audio/<int:audio_id>/delete/', web_views.DeleteAudio.as_view(), name='web-delete-audio'),
]