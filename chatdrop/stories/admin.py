from django.contrib import admin
from . import models

# StoryAdminPanel
class StoryAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'user', 'likes_count', 'content_type', 'posted_on', 'active_until')

admin.site.register(models.Story, StoryAdminPanel)


# StoryViewAdminPanel
class StoryViewAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'story', 'seen_by')

admin.site.register(models.StoryView, StoryViewAdminPanel)
