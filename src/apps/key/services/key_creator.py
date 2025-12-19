from uuid import UUID

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import transaction
from django.utils.timezone import localtime

from apps.balance.models import BalanceHistory
from apps.key.models import Key
from apps.server.models import Server
from apps.tariff.models import Tariff
from apps.user.models import User


class KeyCreator:
    """
    Command to create a new key for a user.
    """

    def __init__(self, *, user_id: UUID, tariff_id: int, title: str | None):
        self._user_id = user_id
        self._tariff_id = tariff_id
        self._title = title

    @transaction.atomic
    def create(self) -> None:
        user = User.objects.filter(id=self._user_id).first()
        tariff = Tariff.objects.filter(id=self._tariff_id).first()

        if not user:
            raise ValueError('User not found')
        if not tariff:
            raise ValueError('Tariff not found')
        if user.balance < tariff.price:
            raise ValueError('Insufficient funds to create key')
        if user.keys.count() >= settings.MAX_KEYS_PER_USER:
            raise ValueError(f'Key limit reached. Maximum allowed keys: {settings.MAX_KEYS_PER_USER}')

        key = Key(
            user=user,
            title=self._title or 'New Key',
            tariff=tariff,
            end_date=localtime() + relativedelta(days=settings.MONTH_DAYS)
        )
        key.save()
        server = Server.objects.order_by('?').first()
        if not server:
            raise ValueError('No servers available to assign the key')
        key.servers.add(server)
        BalanceHistory(
            user=user,
            amount=-tariff.price,
            description='Payment for new key creation'
        ).save()
