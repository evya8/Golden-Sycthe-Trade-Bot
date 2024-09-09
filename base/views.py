from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserSetting, BotOperation, TradeSymbols
from .serializers import UserSerializer, UserSettingSerializer, BotOperationSerializer
from .bot import toggle_bot
import json

# Symbols View
class SymbolsView(APIView):
    def get(self, request):
        symbols_query = TradeSymbols.objects.all()
        symbols = symbols_query.values('symbol', 'type', 'exchange', 'company_name', 'sector')
        return Response({'symbols': list(symbols)}, status=status.HTTP_200_OK)

# Registration View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        user = request.user  # Get the authenticated user from the request
        serializer = UserSerializer(user)  # Serialize the user object
        return Response(serializer.data, status=status.HTTP_200_OK)


# Updated Logout View
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({'message': 'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# User Settings View
class UserSettingsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            user_settings = UserSetting.objects.get(user=user)
        except UserSetting.DoesNotExist:
            user_settings = UserSetting.objects.create(
                user=user,
                alpaca_api_key='',  # Empty string for new users
                alpaca_api_secret='',  # Empty string for new users
                position_size=10,
                filter_sector='',
                filter_symbol='',
                bot_active=False
            )
        # Use the serializer to automatically handle decryption via the model properties
        serializer = UserSettingSerializer(user_settings)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        try:
            user_settings = UserSetting.objects.get(user=user)
        except UserSetting.DoesNotExist:
            user_settings = UserSetting(user=user)

        data = request.data

        # Log the incoming data for debugging
        print("Received data:", data)

        # Handle filter fields (arrays), convert to JSON if necessary
        for key in ['filter_sector', 'filter_symbol']:
            if key in data and isinstance(data[key], list):
                data[key] = json.dumps(data[key])

        # Update only the fields provided in the request
        for key, value in data.items():
            if key in ['alpaca_api_key', 'alpaca_api_secret']:
                # Check if API key and secret are present before setting
                if value:
                    setattr(user_settings, key, value)
                else:
                    print(f"Missing {key} in request data")
            else:
                setattr(user_settings, key, value)

        # Save updated user settings
        user_settings.save()

        # Return the updated settings with decrypted API keys via the serializer
        serializer = UserSettingSerializer(user_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# Bot Operations View
class BotOperationsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operations = BotOperation.objects.filter(user=request.user)
        serializer = BotOperationSerializer(operations, many=True)
        return Response(serializer.data)

# Toggle Bot View
class ToggleBotView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data.get('user_id')  # Get user_id from the request data
            if not user_id:
                return Response({'error': 'User ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

            toggle_bot(user_id)  # Call toggle_bot instead of run_bot
            return Response({'message': 'Bot activation state toggled successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
