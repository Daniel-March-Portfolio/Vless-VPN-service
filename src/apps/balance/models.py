from django.db import models

from apps.server.models import Server
from apps.user.models import User
from config.base_model import BaseModel


class BalanceHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balance_history', verbose_name='User')
    amount = models.IntegerField(verbose_name='Amount')
    description = models.CharField(max_length=255, verbose_name='Description')

    class Meta:
        verbose_name = 'Balance History'
        verbose_name_plural = 'Balance Histories'

    def __str__(self):
        return f"{self.user.username} : {self.amount} ⭐"
