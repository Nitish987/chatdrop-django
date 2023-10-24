from django.contrib import admin
from . import models


# Notification Admin Panel
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'subject', 'type')

admin.site.register(models.Notification, NotificationAdmin)
