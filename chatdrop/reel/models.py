from django.conf import settings
from django.db import models
from utils import generator


# Audio
class Audio(models.Model):
    def _upload_to_path(instance, filename):
        return f'audio/{generator.generate_milli_string()}-{filename}'
    
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    name = models.CharField(default='Audio', max_length=50)
    audio = models.FileField(upload_to=_upload_to_path)
    duration = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now=True)

    @property
    def cdn_url(self):
        return settings.CDN_MEDIA_URL + self.audio.name
    
    @property
    def filename(self):
        return self.audio.name.split('/').pop()
    

# Reel
class Reel(models.Model):
    id = models.CharField(default=generator.generate_identity(), primary_key=True, unique=True, editable=False, max_length=36)
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    reel_type = models.CharField(default='REEL', choices=(('REEL', 'Reel'), ('AD', 'Ad'), ('SPONSOR', 'Sponsor')), max_length=10)
    visibility = models.CharField(default='PUBLIC', choices=(('PUBLIC', 'Public'), ('ONLY_FRIENDS', 'Only Friends'), ('PRIVATE', 'Private')), max_length=30)
    text = models.CharField(default='', max_length=300, blank=True)
    contains_hashtags = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    posted_on = models.DateTimeField(default=None)

    @property
    def is_public(self):
        return self.visibility == 'PUBLIC'
    
    @property
    def is_only_friends(self):
        return self.visibility == 'ONLY_FRIENDS'
    
    @property
    def is_private(self):
        return self.visibility == 'PRIVATE'


# Reel Views
class ReelView(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE)
    seen_by = models.ForeignKey('account.User', on_delete=models.CASCADE)


# Reel HashTags
class ReelHashTag(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE)
    type = models.CharField(default='USER', choices=(('USER', 'User'), ('TAG', 'Tag'), ('URL', 'Url')), max_length=10)
    tag = models.CharField(default='', blank=True, max_length=100)


# Reel Video
class ReelVideo(models.Model):
    def _upload_to_path(instance, filename):
        return f'reel/video/{generator.generate_milli_string()}-{filename}'
    
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE)
    video = models.FileField(upload_to=_upload_to_path)
    thumbnail = models.ImageField(upload_to=_upload_to_path, null=True)
    labels = models.JSONField(default=list)
    audio = models.ForeignKey(Audio, null=True, on_delete=models.DO_NOTHING)
    aspect_ratio = models.FloatField(default=1)

    @property
    def cdn_url(self):
        return settings.CDN_MEDIA_URL + self.video.name
    
    @property
    def cdn_thumbnail_url(self):
        if self.thumbnail is None:
            return None
        return settings.CDN_MEDIA_URL + self.thumbnail.name



# Reel Like
class ReelLike(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE)
    by = models.ForeignKey('account.User', on_delete=models.CASCADE)
    type = models.CharField(default='LIKE', choices=(
        ('LIKE', 'Like'), ('LOVE', 'Love'), ('HAHA', 'Haha'), ('YAY', 'Yay'), ('WOW', 'Wow'), ('SAD', 'Sad'), ('ANGRY', 'Angry')
    ), max_length=10)



# Post Comment
class ReelComment(models.Model):
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE)
    by = models.ForeignKey('account.User', on_delete=models.CASCADE)
    text = models.CharField(default='', max_length=10000)
    likes_count = models.IntegerField(default=0)
    commented_on = models.DateTimeField(auto_now=True)



# Post Sub Comment
class ReelCommentLike(models.Model):
    comment = models.ForeignKey(ReelComment, on_delete=models.CASCADE)
    by = models.ForeignKey('account.User', on_delete=models.CASCADE)
    type = models.CharField(default='LIKE', choices=(
        ('LIKE', 'Like'), ('LOVE', 'Love'), ('HAHA', 'Haha'), ('YAY', 'Yay'), ('WOW', 'Wow'), ('SAD', 'Sad'), ('ANGRY', 'Angry')
    ), max_length=10)

    
