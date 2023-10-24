from django.contrib import admin
from . import models


# ChatGptMessage Admin Model
class ChatGptMessageHolderAdminPanel(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(models.ChatGptMessageHolder, ChatGptMessageHolderAdminPanel)
