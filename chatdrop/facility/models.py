from django.db import models

# Link Preview Model
class LinkPreviewContent(models.Model):
    url = models.TextField(default='')
