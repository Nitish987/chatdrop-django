from django.urls import path
from . import views


urlpatterns = [
    # path('v1/post/add/', views.AddPost.as_view(), name='add-post'), # deprecated
    path('v2/post/add/', views.AddPostV2.as_view(), name='add-post-v2'), # deprecated
    path('v3/post/add/', views.AddPostV3.as_view(), name='add-post-v3'),

    path('v1/post/<str:post_id>/view/', views.SinglePostView.as_view(), name='single-post-view'), # deprecated
    path('v2/post/<str:post_id>/view/', views.SinglePostViewV2.as_view(), name='single-post-view-v2'),

    path('v1/post/<str:post_id>/visibility/', views.ChangePostVisilibity.as_view(), name='add-post-visibility'),

    # path('v1/post/list/', views.ListPost.as_view(), name='list-post'), # deprecated
    path('v2/post/list/', views.ListPostV2.as_view(), name='list-post-v2'), # deprecated
    path('v3/post/list/', views.ListPostV3.as_view(), name='list-post-v3'),

    path('v1/post/<str:post_id>/delete/', views.DeletePost.as_view(), name='delete-post'),
    path('v1/post/<str:post_id>/comment/', views.Comment.as_view(), name='add-and-list-post-comment'),
    path('v1/post/<str:post_id>/comment/<str:comment_id>/delete/', views.DeleteComment.as_view(), name='delete-post-comment'),
    path('v1/post/<str:post_id>/like/', views.Like.as_view(), name='post-like'),
    path('v1/post/comment/<str:comment_id>/like/', views.CommentLike.as_view(), name='post-comment-like'),
]