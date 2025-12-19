from django.db import models, transaction
from django.dispatch import receiver

from apps.balance.models import BalanceHistory
from apps.server.models import Server
from apps.telegram.bot import bot
from apps.user.models import User
from config.base_model import BaseModel


class TelegramPayment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+', verbose_name='User')
    amount = models.IntegerField(verbose_name='Amount')
    message_id = models.CharField(verbose_name='Message ID', null=True, blank=True)
    transaction_id = models.CharField(max_length=255, verbose_name='Transaction ID', null=True, blank=True)
    cancelled = models.BooleanField(default=False, verbose_name='Cancelled')
    do_cancel = models.BooleanField(default=False, verbose_name='Do Cancel')

    class Meta:
        verbose_name = 'Telegram payment'
        verbose_name_plural = 'Telegram payments'

        indexes = [
            models.Index(fields=['message_id'], name='telegram_payment_tx_id_idx'),
        ]

    def __str__(self):
        return f"{self.user.username} : {self.amount} ⭐"


@receiver(models.signals.post_save, sender=TelegramPayment)
@transaction.atomic
def handle_do_cancel(sender, instance: TelegramPayment, created, **kwargs):
    if not created:
        if instance.do_cancel and not instance.cancelled:
            BalanceHistory(
                user=instance.user,
                amount=-instance.amount,
                description=f'Refund for Telegram payment'
            ).save()
            instance.cancelled = True
            instance.save()
            bot.refund_star_payment(
                user_id=instance.user.username,
                telegram_payment_charge_id=instance.transaction_id
            )