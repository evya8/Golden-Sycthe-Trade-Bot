from django.urls import path
from .views import RegisterView, LoginView, UserSettingsView, BotOperationsView, RunBotView , SectorsView, SymbolsView, ExchangesView


urlpatterns = [
   
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/user-settings/', UserSettingsView.as_view(), name='user-settings'),
    path('api/bot-operations/', BotOperationsView.as_view(), name='bot-operations'),
    path('api/run-bot/', RunBotView.as_view(), name='run-bot'),
    path('api/sectors', SectorsView.as_view(), name='sectors'),
    path('api/exchanges', ExchangesView.as_view(), name='exchanges'),
    path('api/symbols', SymbolsView.as_view(), name='symbols'),
    
]
