from django.core.management import BaseCommand

from apps.telegram.views import *  # noqa


class Command(BaseCommand):
    """Run the Telegram bot in polling mode."""

    def add_arguments(self, parser):
        parser.add_argument('--token', type=str, required=False)

    def handle(self, *args, **options):
        bot.token = options['token'] or settings.BOT_TOKEN
        bot.delete_webhook()
        bot.polling(non_stop=True)
