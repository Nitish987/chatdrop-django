from django.contrib import admin
from . import models

# Blocked User Admin Panel
class BlockedUserAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'user', 'blocked_user')

admin.site.register(models.BlockedUser, BlockedUserAdminPanel)


# Reported User Admin Panel
class ReportedUserAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'reported_user', 'message')

admin.site.register(models.ReportedUser, ReportedUserAdminPanel)
