import json

from django.contrib.auth import login
from django.http import HttpResponse
from rest_framework import serializers, permissions
from rest_framework import viewsets
from rest_framework.decorators import action

from apps.key.models import User
from apps.user.telegram_auth import TelegramAuthVariant


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']
        read_only_fields = ['id', ]


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    http_method_names = ['get', 'post']

    def get_permissions(self):
        if self.action == 'login_telegram':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        pass

    @action(detail=False, methods=['post'])
    def login_telegram(self, request):
        user = TelegramAuthVariant(json.loads(request.body)['initData']).auth()
        login(request, user)
        return HttpResponse(status=200)
