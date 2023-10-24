from django.db import models
from account.models import User

# Blocked User
class BlockedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_user')


# Reported User
class ReportedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_by')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_user')
    message = models.TextField(default='', blank=True)
    
