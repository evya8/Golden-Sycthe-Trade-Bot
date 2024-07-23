from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserSetting, BotOperation
from .serializers import UserSerializer, UserSettingSerializer, BotOperationSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
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
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class UserSettingsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        try:
            user_settings = UserSetting.objects.get(user=user)
        except UserSetting.DoesNotExist:
            # If no UserSetting exists, create a default one
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
