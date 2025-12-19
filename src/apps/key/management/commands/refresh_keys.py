from time import sleep

from django.core.management import BaseCommand
from django.utils.timezone import localtime

from apps.key.services.keys_refresher import KeysRefresher


class Command(BaseCommand):
    help = "Create and delete keys on servers as needed."

    def add_arguments(self, parser):
        parser.add_argument('repeat_time_gap', type=int, help='Time gap in seconds to repeat the refresh. 0 - no repeat')

    def handle(self, *args, **options):
        repeat_time_gap = options.get('repeat_time_gap', 0)
        while True:
            self.stdout.write(self.style.NOTICE(f'Refresh keys ({localtime().isoformat()}) ...'))
            key_refresher = KeysRefresher()
            key_refresher.refresh()
            sleep(repeat_time_gap)
            if not repeat_time_gap > 0:
                break
