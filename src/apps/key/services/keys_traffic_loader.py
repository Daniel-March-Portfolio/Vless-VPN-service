from uuid import UUID

import requests
from django.db import transaction

from apps.key.models import Key, KeyTraffic
from apps.server.models import Server
from apps.traffic.models import TrafficUsage


class KeysTrafficLoader:
    """
    Service to load and update traffic data for keys from all servers.
    """

    def load_traffic_data(self) -> None:
        servers = Server.objects.all()
        for server in servers:
            self._load_traffic_from_server(server)

    @transaction.atomic
    def _load_traffic_from_server(self, server: Server) -> None:
        session = requests.Session()
        if not session.post(f'{server.api_url}/login', data={"username": server.api_user, "password": server.api_key}, verify=False).json()['success']:
            raise ConnectionError('Failed to authenticate with the server')
        result = session.get(f'{server.api_url}/panel/api/inbounds/list', verify=False).json()
        inbounds = result.get('obj', [])

        last_keys_traffics = (
            TrafficUsage.objects
            .filter(server=server)
        )
        last_keys_traffics_map = {
            traffic.key_id: (traffic.upload_mb, traffic.download_mb, traffic.total_mb)
            for traffic in last_keys_traffics
        }
        key_ids = set(Key.objects.values_list('id', flat=True))
        (
            TrafficUsage.objects
            .filter(server=server)
            .delete()
        )  # Delete old traffic data for the server
        for inbound in inbounds:
            clients = inbound.get('clientStats', [])
            for client in clients:
                key_id = UUID(client['email'])
                if key_id not in key_ids:
                    continue
                upload_mb = int(client['up'] / 1024 ** 2)
                download_mb = int(client['down'] / 1024 ** 2)
                total_mb = upload_mb + download_mb
                if total_mb == 0:
                    continue
                last_upload_mb, last_download_mb, last_total_mb = last_keys_traffics_map.get(key_id, (0, 0, 0))
                if last_total_mb > total_mb:  # Traffic reset detected
                    last_upload_mb, last_download_mb, last_total_mb = 0, 0, 0
                TrafficUsage(
                    key_id=key_id,
                    server=server,
                    upload_mb=upload_mb,
                    download_mb=download_mb,
                    total_mb=total_mb,
                ).save()
                newly_upload_mb = upload_mb - last_upload_mb
                newly_download_mb = download_mb - last_download_mb
                newly_total_mb = newly_upload_mb + newly_download_mb
                if newly_total_mb > 0:
                    KeyTraffic(
                        key_id=key_id,
                        upload_mb=newly_upload_mb,
                        download_mb=newly_download_mb,
                        total_mb=newly_total_mb,
                    ).save()
