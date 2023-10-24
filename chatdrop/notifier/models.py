from django.db import models


# Notification Model
class Notification(models.Model):
    from_user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='to_user')
    subject = models.CharField(default='', max_length=100)
    body = models.CharField(default='', max_length=200)
    type = models.CharField(default='DEFAULT', choices=(
        ('DEFAULT', 'Default'), 
        ('POST', 'Post'), 
        ('POST_COMMENT', 'Post Comment'), 
        ('POST_LIKE', 'Post Like'), 
        ('POST_COMMENT_LIKE', 'Post Comment Like'), 
        ('REEL', 'Reel'), 
        ('REEL_COMMENT', 'Reel Comment'), 
        ('REEL_LIKE', 'Reel Like'), 
        ('REEL_COMMENT_LIKE', 'Reel Comment Like'), 
        ('FRIEND_REQUEST', 'Friend Request'), 
        ('FOLLOW_REQUEST', 'Follow Request'), 
        ('FOLLOWER', 'Follower'), 
        ('SECRET_CHAT_MESSAGE', 'Secret Chat Message'), 
        ('NORMAL_CHAT_MESSAGE', 'Normal Chat Message')
    ), max_length=30)
    refer = models.CharField(default='', max_length=50, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True, editable=False)
