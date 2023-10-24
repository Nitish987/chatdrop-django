from django.contrib import admin
from . import models

# ReelAdminPanel
class ReelAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'user', 'likes_count', 'comments_count', 'posted_on')

admin.site.register(models.Reel, ReelAdminPanel)


# ReelViewAdminPanel
class ReelViewAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'reel', 'seen_by')

admin.site.register(models.ReelView, ReelViewAdminPanel)


# ReelHashTagsAdminPanel
class ReelHashTagAdminPanel(admin.ModelAdmin):
    list_display = ('reel', 'type')

admin.site.register(models.ReelHashTag, ReelHashTagAdminPanel)


# ReelVideoAdminPanel
class ReelVideoAdminPanel(admin.ModelAdmin):
    list_display = ('reel', 'video')

admin.site.register(models.ReelVideo,ReelVideoAdminPanel)


# ReelLikeAdminPanel
class ReelLikeAdminPanel(admin.ModelAdmin):
    list_display = ('reel', 'by', 'type')

admin.site.register(models.ReelLike, ReelLikeAdminPanel)


# ReelCommentAdminPanel
class ReelCommentAdminPanel(admin.ModelAdmin):
    list_display = ('reel', 'likes_count', 'commented_on')

admin.site.register(models.ReelComment, ReelCommentAdminPanel)


# ReelCommentLikeAdminPanel
class ReelCommentLikeAdminPanel(admin.ModelAdmin):
    list_display = ('comment', 'by', 'type')

admin.site.register(models.ReelCommentLike, ReelCommentLikeAdminPanel)

# AudioAdminPanel
class AudioAdminPanel(admin.ModelAdmin):
    list_display = ('name', 'audio')

admin.site.register(models.Audio, AudioAdminPanel)
