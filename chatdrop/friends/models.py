from django.db import models


# Friend
class Friend(models.Model):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='user')
    friend = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='friend')
    chat_room = models.CharField(max_length=36)
    relation_on = models.DateTimeField(auto_now=True)


# Friend Request
class FriendRequest(models.Model):
    sender = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(default='', max_length=10000)
    request_on = models.DateTimeField(auto_now=True)
