from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.utils.timezone import localtime

from apps.balance.models import BalanceHistory
from apps.key.models import Key


class KeyDeleter:
    """
    Command to delete a user's key.
    """

    def __init__(self, *, key_id: UUID, user_id: UUID):
        self._key_id = key_id
        self._user_id = user_id

    @transaction.atomic
    def delete(self) -> None:
        key = Key.objects.filter(id=self._key_id, user_id=self._user_id).select_related('tariff').first()
        user = key.user

        if not key:
            raise ValueError('Key not found')
        if key.is_active:
            unused_days = (key.end_date - localtime()).days
            unused_days_portion = min(unused_days / settings.MONTH_DAYS, 1.0)

            unused_traffic_portion = (100 - key.used_traffic_percentage) / 100

            refund_portion = min(unused_days_portion, unused_traffic_portion)

            revert_amount = round(key.tariff.price * refund_portion)
            if revert_amount > 0:
                BalanceHistory(
                    user=user,
                    amount=revert_amount,
                    description='Refund for key deletion',
                ).save()
        key.delete()
