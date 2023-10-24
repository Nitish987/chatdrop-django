from django.urls import path
from . import web_views


urlpatterns = [
    path('v3/post/add/', web_views.AddPostV3.as_view(), name='web-add-post-v3'),
    path('v2/post/<str:post_id>/view/', web_views.SinglePostViewV2.as_view(), name='web-single-post-view-v2'),
    path('v1/post/<str:post_id>/visibility/', web_views.ChangePostVisilibity.as_view(), name='web-add-post-visibility'),
    path('v3/post/list/', web_views.ListPostV3.as_view(), name='web-list-post-v3'),
    path('v1/post/<str:post_id>/delete/', web_views.DeletePost.as_view(), name='web-delete-post'),
    path('v1/post/<str:post_id>/comment/', web_views.Comment.as_view(), name='web-add-and-list-post-comment'),
    path('v1/post/<str:post_id>/comment/<str:comment_id>/delete/', web_views.DeleteComment.as_view(), name='web-delete-post-comment'),
    path('v1/post/<str:post_id>/like/', web_views.Like.as_view(), name='web-post-like'),
    path('v1/post/comment/<str:comment_id>/like/', web_views.CommentLike.as_view(), name='web-post-comment-like'),
]