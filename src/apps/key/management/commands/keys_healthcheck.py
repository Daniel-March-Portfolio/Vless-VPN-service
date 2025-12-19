from time import sleep

from django.core.management import BaseCommand
from django.utils.timezone import localtime

from apps.key.services.keys_healthchecker import KeysHealthchecker


class Command(BaseCommand):
    help = "Checks the health of keys in the system."

    def add_arguments(self, parser):
        parser.add_argument('repeat_time_gap', type=int, help='Time gap in seconds to repeat the healthcheck. 0 - no repeat')

    def handle(self, *args, **options):
        repeat_time_gap = options.get('repeat_time_gap', 0)
        while True:
            self.stdout.write(self.style.NOTICE(f'Checking keys health ({localtime().isoformat()}) ...'))
            keys_healthchecker = KeysHealthchecker()
            keys_healthchecker.check()
            sleep(repeat_time_gap)
            if not repeat_time_gap > 0:
                break
