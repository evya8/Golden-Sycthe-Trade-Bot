from django.urls import path
from .views import RegisterView, LogoutView, UserSettingsView, BotOperationsView, ToggleBotView, SymbolsView, UserDetailView , BacktestView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login using SimpleJWT
    path('api/logout/', LogoutView.as_view(), name='logout'),  # Custom logout to blacklist refresh token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh the access token
    path('api/user-settings/', UserSettingsView.as_view(), name='user-settings'),
    path('api/bot-operations/', BotOperationsView.as_view(), name='bot-operations'),
    path('api/toggle-bot/', ToggleBotView.as_view(), name='toggle-bot'),
    path('api/symbols/', SymbolsView.as_view(), name='symbols'),
    path('api/user/', UserDetailView.as_view(), name='user-detail'),  
    path('api/backtest/', BacktestView.as_view(), name='backtest'),


]
