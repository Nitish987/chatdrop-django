from django.contrib import admin
from . import models


# Following Admin Panel
class FollowingAdminPanel(admin.ModelAdmin):
    list_display = ('user', 'follow')

admin.site.register(models.Following, FollowingAdminPanel)


# Follow Request Admin Panel
class FollowRequestAdminPanel(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'request_on')

admin.site.register(models.FollowRequest, FollowRequestAdminPanel)


