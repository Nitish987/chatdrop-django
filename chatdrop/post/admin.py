from django.contrib import admin
from . import models

# PostAdminPanel
class PostAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'user', 'likes_count', 'comments_count', 'content_type', 'posted_on')

admin.site.register(models.Post, PostAdminPanel)


# PostHashTagsAdminPanel
class PostHashTagAdminPanel(admin.ModelAdmin):
    list_display = ('post', 'type')

admin.site.register(models.PostHashTag, PostHashTagAdminPanel)


# PostPhotoAdminPanel
class PostPhotoAdminPanel(admin.ModelAdmin):
    list_display = ('post', 'photo')

admin.site.register(models.PostPhoto, PostPhotoAdminPanel)


# PostVideoAdminPanel
class PostVideoAdminPanel(admin.ModelAdmin):
    list_display = ('post', 'video', 'thumbnail')

admin.site.register(models.PostVideo, PostVideoAdminPanel)


# PostLikeAdminPanel
class PostLikeAdminPanel(admin.ModelAdmin):
    list_display = ('post', 'by', 'type')

admin.site.register(models.PostLike, PostLikeAdminPanel)


# PostCommentAdminPanel
class PostCommentAdminPanel(admin.ModelAdmin):
    list_display = ('post', 'likes_count', 'commented_on')

admin.site.register(models.PostComment, PostCommentAdminPanel)


# PostCommentLikeAdminPanel
class PostCommentLikeAdminPanel(admin.ModelAdmin):
    list_display = ('comment', 'by', 'type')

admin.site.register(models.PostCommentLike, PostCommentLikeAdminPanel)
