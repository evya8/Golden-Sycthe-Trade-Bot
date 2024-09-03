from django.urls import path
from .views import  RegisterView, LoginView, LogoutView, UserSettingsView, BotOperationsView, ToggleBotView, SymbolsView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
   
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user-settings/', UserSettingsView.as_view(), name='user-settings'),
    path('api/bot-operations/', BotOperationsView.as_view(), name='bot-operations'),
    path('api/toggle-bot/', ToggleBotView.as_view(), name='toggle-bot'),
    path('api/symbols/', SymbolsView.as_view(), name='symbols'),

    
]
