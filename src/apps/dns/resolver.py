import logging
import os
import random
import socketserver
import struct
import traceback

from django.conf import settings
from django.core.cache.backends.redis import RedisCacheClient

from apps.dns.models import DNSRecord

logging.basicConfig(
    level=os.environ.get('LOGLEVEL', 'INFO').upper(),
    format='%(asctime)s %(message)s',
    datefmt='%m.%d.%Y %H:%M:%S'
)

FLAGS = b'\x81\x80'
QDCOUNT = b'\x00\x01'
NSCOUNT = b'\x00\x00'
ARCOUNT = b'\x00\x00'
NAME_PTR = b'\xc0\x0c'
TYPE_A = b'\x00\x01'
CLASS_IN = b'\x00\x01'
TTL = b'\x00\x00\x00\x0a'  # 10 секунд


class Configuration:
    def __init__(self):
        self._domain_to_ip: dict[str, set[str]] = {}
        self._redis = RedisCacheClient(
            servers=[settings.REDIS_CONNECTION_STRING],
        )

    def get_domain_ip(self, domain: str) -> str | None:
        domain = domain.lower()[:-1]
        ips = self._redis.get(domain, None)
        if ips is None:
            ips = DNSRecord.objects.filter(domain=domain).values_list('ip_address', flat=True)
        if ips:
            self._redis.set(domain, ips, timeout=10)
        return random.choice(list(ips)) if ips else None


config = Configuration()


class DNSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]
        rdata = b''
        rdlength = b'\x00\x00'
        ancount = b'\x00\x00'
        query = b'\x00\x00'
        qtype = b'\x00\x00'
        qclass = b'\x00\x00'
        transaction_id = b'\x00\x00'
        try:
            transaction_id = data[:2]

            query_start = 12
            query_end = data.find(b'\x00', query_start) + 1
            query = data[query_start:query_end]
            qtype = data[query_end:query_end + 2]
            qclass = data[query_end + 2:query_end + 4]
            domain = self.extract_domain(data)
            if not domain.endswith('.'):
                domain += '.'
            ip = config.get_domain_ip(domain)

            if ip is not None:
                rdlength = b'\x00\x04'
                ancount = b'\x00\x01'
                rdata = struct.pack('!BBBB', *map(int, ip.split('.')))
                logging.info(f"Resolved {domain} to {ip}")
            else:
                logging.warning(f"No record found for {domain}")

        except:
            logging.error(traceback.format_exc())
            logging.error(f'Data: {data}')
        response = b''.join(
            [transaction_id, FLAGS, QDCOUNT, ancount, NSCOUNT, ARCOUNT,
             query, qtype, qclass, NAME_PTR, TYPE_A, CLASS_IN, TTL,
             rdlength, rdata]
        )

        socket.sendto(response, self.client_address)

    @staticmethod
    def extract_domain(request: bytes) -> str:
        query_start = 12
        domain_parts = []
        length = request[query_start]

        while length != 0:
            if length > 0:
                domain_parts.append(
                    request[query_start + 1:query_start + 1 + length].decode())
            query_start += length + 1
            length = request[query_start]

        return '.'.join(domain_parts)
