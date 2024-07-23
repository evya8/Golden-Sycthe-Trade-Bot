from django.urls import path
from .views import RegisterView, LoginView, UserSettingsView, BotOperationsView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/user-settings/', UserSettingsView.as_view(), name='user-settings'),
    path('api/bot-operations/', BotOperationsView.as_view(), name='bot-operations'),
]
