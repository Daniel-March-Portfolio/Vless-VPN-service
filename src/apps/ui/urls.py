from django.urls import path

from apps.ui.views import main, key, balance, auth

urlpatterns = [
    path('', main),
    path('auth/', auth),
    path('keys/<uuid:pk>/', key),
    path('balance/', balance),
]
