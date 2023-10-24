from django.conf import settings
from django.utils import timezone
from django.db import models
from utils import generator


# Story
class Story(models.Model):
    def _upload_to_path(instance, filename):
        return f'story/{generator.generate_milli_string()}-{filename}'
    
    id = models.CharField(default=generator.generate_identity(), primary_key=True, unique=True, editable=False, max_length=36)
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    content_type = models.CharField(default='TEXT', choices=(('TEXT', 'Text'), ('PHOTO', 'Photo'), ('VIDEO', 'Video')), max_length=20)
    content = models.FileField(upload_to=_upload_to_path)
    text = models.CharField(default='', max_length=1000, blank=True)
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    posted_on = models.DateTimeField(default=None)
    active_until = models.DateTimeField(default=None)

    @property
    def is_active(self):
        return self.active_until >= timezone.now()
    
    @property
    def content_cdn_url(self):
        return settings.CDN_MEDIA_URL + self.content.name




# Story Views
class StoryView(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    seen_by = models.ForeignKey('account.User', on_delete=models.CASCADE)