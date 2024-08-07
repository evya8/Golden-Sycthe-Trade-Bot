from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings
import json


class TradeSymbols(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    type = models.CharField(max_length=10)
    description = models.CharField(max_length=255, blank=True, null=True)
    exchange = models.CharField(max_length=50, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.symbol

class UserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    _alpaca_api_key = models.BinaryField(default=b'')  
    _alpaca_api_secret = models.BinaryField(default=b'') 
    position_size = models.FloatField(default=0.1,help_text="Percentage of equity to allocate to each position")
    filter_type = models.CharField(max_length=10, default='both', blank=True, null=True)
    filter_sector = models.CharField(max_length=50, default='',blank=True, null=True)
    filter_exchange = models.CharField(max_length=50, default='',blank=True, null=True)
    filter_symbol = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def set_filter_symbol(self, lst):
        self.filter_symbol = json.dumps(lst)

    def get_filter_symbol(self):
        return json.loads(self.filter_symbol)

    @property
    def alpaca_api_key(self):
        return Fernet(settings.ENCRYPTION_KEY).decrypt(self._alpaca_api_key).decode()

    @alpaca_api_key.setter
    def alpaca_api_key(self, value):
        self._alpaca_api_key = Fernet(settings.ENCRYPTION_KEY).encrypt(value.encode())

    @property
    def alpaca_api_secret(self):
        return Fernet(settings.ENCRYPTION_KEY).decrypt(self._alpaca_api_secret).decode()

    @alpaca_api_secret.setter
    def alpaca_api_secret(self, value):
        self._alpaca_api_secret = Fernet(settings.ENCRYPTION_KEY).encrypt(value.encode())

    def __str__(self):
        return f"{self.user.username}'s settings"


class BotOperation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=50)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.operation_type} - {self.timestamp}"