from django.db import models
from django.contrib.auth.models import User

class UserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alpaca_api_key = models.CharField(max_length=100)
    alpaca_api_secret = models.CharField(max_length=100)
    position_size = models.FloatField(help_text="Percentage of equity to allocate to each position")

    def __str__(self):
        return f"{self.user.username}'s settings"

class BotOperation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=50)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.operation_type} - {self.timestamp}"