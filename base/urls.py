from django.urls import path
from .views import filtered_symbols, RegisterView, LoginView, LogoutView, UserSettingsView, BotOperationsView, RunBotView , SectorsView, SymbolsView, ExchangesView
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
    path('api/run-bot/', RunBotView.as_view(), name='run-bot'),
    path('api/sectors/', SectorsView.as_view(), name='sectors'),
    path('api/exchanges/', ExchangesView.as_view(), name='exchanges'),
    path('api/symbols/', SymbolsView.as_view(), name='symbols'),
    path('api/filtered-symbols/', filtered_symbols, name='filtered-symbols'),

    
]
