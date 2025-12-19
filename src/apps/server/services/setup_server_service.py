from uuid import UUID

from django.conf import settings
from py3xui import Api, Inbound
from py3xui.inbound import Settings, Sniffing, StreamSettings

from apps.server.models import Server


class SetupServerService:
    """
    Service for setting up a server with a predefined inbound configuration.
    """

    def setup(self, uuid: UUID) -> None:
        server = Server.objects.get(pk=uuid)
        api = Api(server.api_url, server.api_user, server.api_key, use_tls_verify=False)
        api.login()
        inbounds = api.inbound.get_list()
        for inbound in inbounds:
            api.inbound.delete(inbound.id)
        api.inbound.add(
            Inbound(
                enable=True,
                remark='AutoSetup',
                port=settings.VLESS_PORT,
                protocol='vless',
                settings=Settings(),
                stream_settings=StreamSettings(
                    security='reality',
                    network='tcp',
                    tcp_settings={'acceptProxyProtocol': False, 'header': {'type': 'none'}},
                    reality_settings={
                        'dest': 'wikipedia.org:443',
                        'maxClient': '',
                        'maxTimediff': 0,
                        'minClient': '',
                        'privateKey': settings.VLESS_PRIVATE_KEY,
                        'serverNames': ['wikipedia.org', 'www.wikipedia.org'],
                        'settings': {'fingerprint': 'random',
                                     'publicKey': settings.VLESS_PUBLIC_KEY,
                                     'serverName': '',
                                     'spiderX': '/'},
                        'shortIds': settings.VLESS_SHORT_IDS,
                        'show': False,
                        'xver': 0
                    }
                ),
                sniffing=Sniffing(enabled=False),
            )
        )


