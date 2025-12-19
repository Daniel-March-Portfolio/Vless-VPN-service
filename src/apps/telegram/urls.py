from django.urls import path

from apps.telegram.views import telegram_webhook

urlpatterns = [
    path('', telegram_webhook),
]
