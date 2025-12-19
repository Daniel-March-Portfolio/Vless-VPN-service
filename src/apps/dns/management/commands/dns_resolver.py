import logging
import socketserver

from django.core.management import BaseCommand

from apps.dns.resolver import DNSHandler


class Command(BaseCommand):
    help = "Starts a simple DNS resolver server."

    def handle(self, *args, **options):
        server = socketserver.UDPServer(("0.0.0.0", 8053), DNSHandler)
        logging.info("DNS Server is running...")
        while True:
            try:
                server.handle_request()
            except Exception as e:
                logging.error(f"Error handling request {e}")
