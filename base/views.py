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
from .bot import run_bot


class SymbolsView(APIView):
    def get(self, request):
        sector = request.query_params.get('sector', None)
        exchange = request.query_params.get('exchange', None)
        type = request.query_params.get('type', None)

        symbols_query = TradeSymbols.objects.all()

        if sector:
            symbols_query = symbols_query.filter(sector=sector)
        if exchange:
            symbols_query = symbols_query.filter(exchange=exchange)
        if type:
            symbols_query = symbols_query.filter(type=type)

        symbols = symbols_query.values('symbol', 'company_name')

        # Optional: Provide a message if filters were applied or if it's the full list
        if not sector and not exchange and not type:
            message = "All symbols retrieved."
        else:
            message = f"Filtered symbols based on: " \
                      f"{'sector: ' + sector if sector else ''} " \
                      f"{'exchange: ' + exchange if exchange else ''} " \
                      f"{'type: ' + type if type else ''}".strip()

        return Response({'message': message, 'symbols': symbols}, status=status.HTTP_200_OK)


class ExchangesView(APIView):
    def get(self, request):
        exchanges = TradeSymbols.objects.values_list('exchange', flat=True).distinct()
        return Response({'exchanges': exchanges}, status=status.HTTP_200_OK)


class SectorsView(APIView):
    def get(self, request):
        sectors = TradeSymbols.objects.values_list('sector', flat=True).distinct()
        return Response({'sectors': sectors}, status=status.HTTP_200_OK)


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
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'User logged in successfully'
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

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
            )
        serializer = UserSettingSerializer(user_settings)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        try:
            user_settings = UserSetting.objects.get(user=user)
        except UserSetting.DoesNotExist:
            user_settings = UserSetting(user=user)
        
        serializer = UserSettingSerializer(user_settings, data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BotOperationsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operations = BotOperation.objects.filter(user=request.user)
        serializer = BotOperationSerializer(operations, many=True)
        return Response(serializer.data)
    
class RunBotView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            
            run_bot()  
            return Response({'message': 'Bot run initiated successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
