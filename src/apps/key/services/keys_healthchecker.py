from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils.timezone import localtime

from apps.key.models import Key


class KeysHealthchecker:
    """
    Service to check and manage the health of keys in the system.
    It checks if keys need to be auto-renewed or deactivated based on their end date and user's balance.
    """

    @transaction.atomic
    def check(self) -> None:
        self._stop_no_auto_renew()
        self._auto_renew()

    def _auto_renew(self):
        keys = Key.objects.filter(is_active=True, auto_renew=True, end_date__lte=localtime() + relativedelta(hours=1)).select_related('user', 'tariff')
        account_balances = {}
        for key in keys:
            balance = account_balances.get(key.user, None) or key.user.balance
            account_balances[key.user] = balance
            account_balances[key.user] -= self._renew_key(key=key, account_balance=account_balances[key.user])

    def _renew_key(self, *, key: Key, account_balance: int) -> int:
        balance_change = 0
        key.is_active = False
        if account_balance < key.tariff.price:
            key.save(update_fields=['is_active'])
        else:
            key.refuel(description='Auto-renewal of the key')
            balance_change = -key.tariff.price
        return balance_change

    def _stop_no_auto_renew(self):
        keys = Key.objects.filter(is_active=True, auto_renew=False, end_date__lt=localtime())
        for key in keys:
            key.is_active = False
            key.save()
