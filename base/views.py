from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserSetting, BotOperation , TradeSymbols
from .serializers import UserSerializer, UserSettingSerializer, BotOperationSerializer
from .bot import toggle_bot  
import json

class SymbolsView(APIView):
    def get(self, request):
        symbols_query = TradeSymbols.objects.all()
        symbols = symbols_query.values('symbol', 'type', 'exchange', 'company_name', 'sector')
        return Response({'symbols': list(symbols)}, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data,
                'message': 'User logged in successfully'
            }, status=status.HTTP_200_OK)
        
        print("Authentication failed for user: ", username)  # Debugging statement
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
                alpaca_api_key='',
                alpaca_api_secret='',
                position_size=10,
                filter_sector='',
                filter_symbol='',
                bot_active=False
                
            )
        serializer = UserSettingSerializer(user_settings)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        try:
            user_settings = UserSetting.objects.get(user=user)
        except UserSetting.DoesNotExist:
            user_settings = UserSetting(user=user)

        # Log the incoming data
        print("Received data:", request.data)

        data = request.data

        # Ensure arrays are correctly handled for multiselect fields
        for key in ['filter_sector', 'filter_symbol']:
            if key in data and isinstance(data[key], list):
                data[key] = json.dumps(data[key])

        # Update only the fields provided in the request
        for key, value in data.items():
            setattr(user_settings, key, value)

        user_settings.save()
        serializer = UserSettingSerializer(user_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BotOperationsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operations = BotOperation.objects.filter(user=request.user)
        serializer = BotOperationSerializer(operations, many=True)
        return Response(serializer.data)
    
class ToggleBotView(APIView):  # Updated view to handle toggling the bot
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
