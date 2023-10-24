from django.contrib import admin
from . import models


# Friend Admin Panel
class FriendAdminPanel(admin.ModelAdmin):
    list_display = ('user', 'friend', 'chat_room', 'relation_on')

admin.site.register(models.Friend, FriendAdminPanel)

# Friend Request Admin Panel
class FriendRequestAdminPanel(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'request_on')

admin.site.register(models.FriendRequest, FriendRequestAdminPanel)
