"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from apps.telegram.bot import bot

urlpatterns = []
if settings.IS_API_MODE:
    urlpatterns.extend([
        path('admin/', admin.site.urls),
        path('', include('apps.ui.urls')),
        path('api/', include('apps.key.urls')),
        path('api/', include('apps.user.urls')),
        path('api/', include('apps.balance.urls')),
    ])
    if settings.BOT_WEBHOOK:
        urlpatterns.append(path(settings.BOT_WEBHOOK, include('apps.telegram.urls')))
        print('Old webhook deleted:', bot.delete_webhook())
        print(f'New webhook created on https://{settings.DOMAIN}/{settings.BOT_WEBHOOK}: ', bot.set_webhook(url=f'https://{settings.DOMAIN}/{settings.BOT_WEBHOOK}'))
