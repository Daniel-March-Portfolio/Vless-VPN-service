from time import sleep

from django.core.management import BaseCommand
from django.utils.timezone import localtime

from apps.key.services.keys_traffic_loader import KeysTrafficLoader


class Command(BaseCommand):
    help = 'Load keys traffic data from servers'

    def add_arguments(self, parser):
        parser.add_argument('repeat_time_gap', type=int, help='Time gap in seconds to repeat traffic loading. 0 - no repeat')

    def handle(self, *args, **options):
        repeat_time_gap = options.get('repeat_time_gap', 0)
        while True:
            self.stdout.write(self.style.NOTICE(f'Loading keys traffic ({localtime().isoformat()}) ...'))
            keys_traffic_loader = KeysTrafficLoader()
            keys_traffic_loader.load_traffic_data()
            sleep(repeat_time_gap)
            if not repeat_time_gap > 0:
                break
