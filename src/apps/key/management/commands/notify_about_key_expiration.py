from datetime import timedelta
from time import sleep

from django.core.management import BaseCommand
from django.db import transaction
from django.utils.timezone import localtime

from apps.key.models import Key, KeyExpNotifications
from apps.telegram.bot import bot


class Command(BaseCommand):
    help = 'Notify users about key expiration'

    def add_arguments(self, parser):
        parser.add_argument('repeat_time_gap', type=int, help='Time gap in seconds to repeat the healthcheck. 0 - no repeat')

    def handle(self, *args, **options):
        repeat_time_gap = options.get('repeat_time_gap', 0)
        while True:
            self._cycle()
            if repeat_time_gap <= 0:
                break
            sleep(repeat_time_gap)

    def _cycle(self):
        now = localtime()
        keys = Key.objects.filter(
            is_active=True,
            end_date__gt=now,
            end_date__lte=now + timedelta(days=3)
        ).select_related('user', 'tariff')
        for key in keys:
            is_notified_recently = self._is_notified_recently(key)
            if not is_notified_recently:
                self._notify_user_about_key_expiration(key)

    @transaction.atomic
    def _notify_user_about_key_expiration(self, key: Key) -> None:
        notification, is_created = (
            KeyExpNotifications.objects
            .get_or_create(
                key=key,
                defaults={'notified_at': localtime()}
            )
        )
        if not is_created:
            notification.notified_at = localtime()
            notification.save(update_fields=['notified_at'])
        text = (
            f"🔑 Your rey '{key.title}' expiring on {key.end_date.strftime('%d.%m.%Y')}.\n"
        )
        if key.auto_renew:
            text += (
                "✅ Auto-renewal is enabled. Your key will be automatically renewed if you have sufficient funds in your account.\n"
                f"Renewal cost: {key.tariff.price}⭐\n"
                f"💰 Current balance: {key.user.balance}⭐\n\n"
                f"You can disable auto-renewal in the key settings.\n"
            )
        else:
            text += (
                "⚠️ Auto-renewal is disabled.\n"
                "You can enable auto-renewal in the key settings or renew the key manually after it expires.\n"
            )


        bot.send_message(
            chat_id=key.user.username,
            text=text
        )

    def _is_notified_recently(self, key: Key) -> bool:
        return (
            KeyExpNotifications.objects
            .filter(
                key=key,
                notified_at__gt=localtime() - timedelta(days=1)
            )
            .exists()
        )
