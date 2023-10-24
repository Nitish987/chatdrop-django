from django.db import models


# Following
class Following(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='current_user')
    follow = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='following_user')


# Following Request
class FollowRequest(models.Model):
    sender = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='following_sender')
    receiver = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='following_receiver')
    message = models.CharField(default='', max_length=10000)
    request_on = models.DateTimeField(auto_now=True)
