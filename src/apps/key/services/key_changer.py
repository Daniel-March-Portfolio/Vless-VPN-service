from uuid import UUID

from apps.balance.models import BalanceHistory
from apps.key.models import Key
from apps.tariff.models import Tariff


class KeyChanger:
    """
    Command to change the key.
    """

    def __init__(self, *, key_id: UUID, user_id: UUID, tariff_id: UUID | None = None, auto_renew: bool | None = None):
        self._key_id = key_id
        self._user_id = user_id
        self._tariff_id = tariff_id
        self._auto_renew = auto_renew

    def change(self) -> None:
        key = Key.objects.filter(id=self._key_id, user_id=self._user_id).first()
        new_tariff = Tariff.objects.filter(id=self._tariff_id or key.tariff.id).first()
        user = key.user

        if not key:
            raise ValueError('Key not found')
        if not key.is_active:
            raise ValueError('Key is not active')
        if not new_tariff:
            raise ValueError('Tariff not found')
        if key.tariff != new_tariff:
            if new_tariff.price > key.tariff.price:
                price_difference = new_tariff.price - key.tariff.price
                if user.balance < price_difference:
                    raise ValueError('Insufficient funds for tariff change')
                BalanceHistory(
                    user=user,
                    amount=-price_difference,
                    description='Additional payment for changing to a more expensive tariff'
                ).save()
            else:
                price_difference = key.tariff.price - new_tariff.price
                if key.used_traffic > new_tariff.traffic:
                    raise ValueError('Used traffic exceeds the new tariff limit')
                BalanceHistory(
                    user=user,
                    amount=price_difference,
                    description='Refund for changing to a cheaper tariff'
                ).save()
            key.tariff = new_tariff
        if self._auto_renew is not None:
            key.auto_renew = self._auto_renew
        key.save()
