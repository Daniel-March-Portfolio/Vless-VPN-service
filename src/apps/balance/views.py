from django.db import transaction
from rest_framework import serializers
from rest_framework import viewsets
from telebot.types import LabeledPrice

from apps.balance.models import BalanceHistory
from apps.telegram.bot import bot
from apps.telegram.models import TelegramPayment


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceHistory
        fields = ['id', 'amount', 'description']
        read_only_fields = ['id', ]


class BalanceViewSet(viewsets.ModelViewSet):
    serializer_class = BalanceSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return BalanceHistory.objects.filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer: BalanceSerializer):
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        if amount > 0:
            telegram_payment = TelegramPayment(
                user=self.request.user,
                amount=amount,
            )
            telegram_payment.save()
            message = bot.send_invoice(
                chat_id=self.request.user.username,
                title="Balance top-up",
                description="Service balance top-up",
                invoice_payload=str(telegram_payment.id),
                provider_token="",
                currency="XTR",
                prices=[
                    LabeledPrice(
                        amount=amount,
                        label="Service balance top-up"
                    )
                ],
            )
            telegram_payment.message_id = message.message_id
            telegram_payment.save(update_fields=['message_id'])
