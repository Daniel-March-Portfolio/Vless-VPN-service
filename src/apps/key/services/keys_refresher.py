from django.db import transaction
from django.db.models import QuerySet
from py3xui import Api, Inbound, Client

from apps.dns.models import DNSRecord
from apps.key.models import Key
from apps.server.models import Server
from apps.server.services.setup_server_service import SetupServerService
from apps.traffic.models import TrafficUsage


class KeysRefresher:
    """
    Service for refreshing keys on all servers and updating DNS records.
    """

    def __init__(self):
        self._server_apis = {}

    @transaction.atomic
    def refresh(self) -> None:
        servers = self._get_servers()
        keys = self._create_keys_on_servers(servers)
        self._update_dns(keys)

    @classmethod
    def _get_servers(cls) -> QuerySet[Server]:
        servers = Server.objects.all()
        return servers

    def _create_keys_on_servers(self, servers: QuerySet[Server]) -> list[Key]:
        """
        Creates or updates keys on the given servers.
        """
        all_keys = []
        for server in servers:
            api = self._get_server_api(server)
            inbound = self._get_or_create_inbound(server)
            keys = self._get_server_keys(server)
            inbound.settings.clients = []
            for key in keys:
                last_usage_mb = self._get_server_key_used_traffic_mb(server, key)
                inbound.settings.clients.append(
                    Client(
                        id=str(key.id),
                        flow="xtls-rprx-vision",
                        email=str(key.id),
                        enable=key.is_active,
                        total_gb=((key.tariff.traffic - key.used_traffic) + last_usage_mb) * 1024 * 1024 # Принимает в байтах
                    )
                )
            api.inbound.update(inbound.id, inbound)
            all_keys.extend(keys)
        return all_keys

    def _get_server_keys(self, server: Server) -> QuerySet[Key]:
        keys = Key.objects.filter(is_active=True, servers=server).select_related('tariff')
        return keys

    def _get_or_create_inbound(self, server: Server) -> Inbound:
        """
        Retrieves or creates an inbound on the server.
        """
        inbound = self._get_inbound(server)
        if not inbound:
            SetupServerService().setup(server.id)
            inbound = self._get_inbound(server)
        if not inbound:
            raise ConnectionError('Failed to create inbound on server')
        return inbound

    def _get_inbound(self, server: Server) -> Inbound | None:
        """
        Retrieves the inbound on the server listening on port 443.
        """
        api = self._get_server_api(server)
        inbounds = api.inbound.get_list()
        for inbound in inbounds:
            if inbound.port == 443:
                return inbound
        return None

    def _get_server_api(self, server: Server):
        """
        Retrieves or creates an API client for the given server.
        """
        if server.id not in self._server_apis:
            api = Api(server.api_url, server.api_user, server.api_key, use_tls_verify=False)
            api.login()
            self._server_apis[server.id] = api
        return self._server_apis[server.id]

    def _get_server_key_used_traffic_mb(self, server: Server, key: Key) -> int:
        """
        Retrieves the used traffic in MB for the given key on the specified server.
        """
        last_usage = TrafficUsage.objects.filter(server=server, key_id=key.id).first()
        if not last_usage:
            return 0
        return last_usage.total_mb

    def _update_dns(self, keys: list[Key]):
        DNSRecord.objects.all().delete()
        for key in keys:
            for server in key.servers.all():
                DNSRecord(
                    domain=key.domain,
                    ip_address=server.ip_address,
                ).save()
