from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum

from apps.server.models import Server


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, verbose_name="ID")

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    @property
    def balance(self) -> int:
        balance = self.balance_history.aggregate(total_mb=Sum('amount'))['total_mb'] or 0
        return balance
