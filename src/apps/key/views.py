from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action

from apps.key.models import Key
from apps.key.services.key_changer import KeyChanger
from apps.key.services.key_creator import KeyCreator
from apps.key.services.key_deleter import KeyDeleter


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ['id', 'title', 'tariff', 'auto_renew']
        read_only_fields = ['id', ]


class KeyViewSet(viewsets.ModelViewSet):
    serializer_class = KeySerializer
    http_method_names = ['get', 'patch', 'delete', 'post']

    def get_queryset(self):
        return Key.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        try:
            KeyDeleter(key_id=instance.id, user_id=self.request.user.id).delete()
        except ValueError as e:
            raise serializers.ValidationError({'error': str(e)})

    def perform_update(self, serializer):
        KeyChanger(
            key_id=serializer.instance.id,
            user_id=self.request.user.id,
            tariff_id=serializer.validated_data.get('tariff', None).id if 'tariff' in serializer.validated_data else None,
            auto_renew=serializer.validated_data.get('auto_renew', None),
        ).change()

    def perform_create(self, serializer):
        KeyCreator(
            user_id=self.request.user.id,
            title=serializer.validated_data.get('title', None),
            tariff_id=serializer.validated_data.get('tariff', None).id if 'tariff' in serializer.validated_data else None,
        ).create()

    @action(detail=True, methods=['post'])
    def refuel(self, request, pk):
        key = get_object_or_404(Key, pk=pk)
        key.refuel(description='Key refueled by user request')
        return HttpResponse(status=200)
