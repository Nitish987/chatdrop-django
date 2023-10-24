from django.db import models


# Chatgpt message holder Model
class ChatGptMessageHolder(models.Model):
    user = models.ForeignKey("account.User", on_delete=models.CASCADE)
    messages = models.JSONField(default=list)