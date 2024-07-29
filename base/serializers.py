from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserSetting, BotOperation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = [
            'alpaca_api_key', 
            'alpaca_api_secret', 
            'position_size', 
            'filter_type', 
            'filter_sector', 
            'filter_exchange', 
            'specific_assets'
        ]
    
    def validate_position_size(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Position size must be between 0 and 100.")
        return value

    def validate_specific_assets(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Specific assets must be a list.")
        for symbol in value:
            if not isinstance(symbol, str):
                raise serializers.ValidationError("Each asset symbol must be a string.")
        return value
    
    
class BotOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotOperation
        fields = '__all__'
