from django.conf import settings
from django.db import models
from utils import generator


# Post
class Post(models.Model):
    id = models.CharField(default=generator.generate_identity(), primary_key=True, unique=True, editable=False, max_length=36)
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    post_type = models.CharField(default='POST', choices=(('POST', 'Post'), ('AD', 'Ad'), ('SPONSOR', 'Sponsor')), max_length=10)
    visibility = models.CharField(default='PUBLIC', choices=(('PUBLIC', 'Public'), ('ONLY_FRIENDS', 'Only Friends'), ('PRIVATE', 'Private')), max_length=30)
    link = models.TextField(default='', blank=True)
    text = models.CharField(default='', max_length=10000, blank=True)
    content_type = models.CharField(default='TEXT', choices=(
        ('TEXT', 'Text'), ('PHOTO', 'Photo'), ('VIDEO', 'Video'), ('TEXT_PHOTO', 'Text & Photo'), ('TEXT_VIDEO', 'Text & Video ')
    ), max_length=20)
    contains_hashtags = models.BooleanField(default=False)
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



# Post HashTags
class PostHashTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    type = models.CharField(default='USER', choices=(('USER', 'User'), ('TAG', 'Tag'), ('URL', 'Url')), max_length=10)
    tag = models.CharField(default='', blank=True, max_length=100)



# Post Photo
class PostPhoto(models.Model):
    def _upload_to_path(instance, filename):
        return f'post/photo/{generator.generate_milli_string()}-{filename}'

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=_upload_to_path)
    labels = models.JSONField(default=list)
    aspect_ratio = models.FloatField(default=1)

    @property
    def cdn_url(self):
        return settings.CDN_MEDIA_URL + self.photo.name



# Post Video
class PostVideo(models.Model):
    def _upload_to_path(instance, filename):
        return f'post/video/{generator.generate_milli_string()}-{filename}'
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    video = models.FileField(upload_to=_upload_to_path)
    thumbnail = models.ImageField(upload_to=_upload_to_path, null=True)
    labels = models.JSONField(default=list)
    aspect_ratio = models.FloatField(default=1)

    @property
    def cdn_url(self):
        return settings.CDN_MEDIA_URL + self.video.name
    
    @property
    def cdn_thumbnail_url(self):
        if self.thumbnail == None:
            return None
        return settings.CDN_MEDIA_URL + self.thumbnail.name



# Post Like
class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    by = models.ForeignKey('account.User', on_delete=models.CASCADE)
    type = models.CharField(default='LIKE', choices=(
        ('LIKE', 'Like'), ('LOVE', 'Love'), ('HAHA', 'Haha'), ('YAY', 'Yay'), ('WOW', 'Wow'), ('SAD', 'Sad'), ('ANGRY', 'Angry')
    ), max_length=10)



# Post Comment
class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    by = models.ForeignKey('account.User', on_delete=models.CASCADE)
    text = models.CharField(default='', max_length=10000)
    likes_count = models.IntegerField(default=0)
    commented_on = models.DateTimeField(auto_now=True)



# Post Sub Comment
class PostCommentLike(models.Model):
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE)
    by = models.ForeignKey('account.User', on_delete=models.CASCADE)
    type = models.CharField(default='LIKE', choices=(
        ('LIKE', 'Like'), ('LOVE', 'Love'), ('HAHA', 'Haha'), ('YAY', 'Yay'), ('WOW', 'Wow'), ('SAD', 'Sad'), ('ANGRY', 'Angry')
    ), max_length=10)

