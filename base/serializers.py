from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserSetting, BotOperation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password' ,'id', 'first_name', 'last_name', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class UserSettingSerializer(serializers.ModelSerializer):
    alpaca_api_key = serializers.CharField( read_only=True)
    alpaca_api_secret = serializers.CharField( read_only=True)

    class Meta:
        model = UserSetting
        fields = [
            'alpaca_api_key', 
            'alpaca_api_secret', 
            'bot_active',
            'position_size', 
            'filter_sector', 
            'filter_symbol'
        ]
    
    def validate_position_size(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Position size must be between 0 and 100.")
        return value
    
class BotOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotOperation
        fields = ['id', 'user', 'stock_symbol', 'stage', 'status', 'reason', 'timestamp']
