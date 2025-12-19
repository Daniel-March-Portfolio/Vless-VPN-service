from django.db import models

from config.base_model import BaseModel


class Tariff(BaseModel):
    title = models.CharField(max_length=255, verbose_name='Title')
    price = models.PositiveIntegerField(verbose_name='Price')
    traffic = models.IntegerField(verbose_name='Traffic (MB)')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Tariff'
        verbose_name_plural = 'Tariffs'

    def __str__(self):
        return f'{self.title}'

    @property
    def traffic_display(self) -> str:
        mb_amount = self.traffic
        gb_amount = self.traffic / 1024
        tb_amount = gb_amount / 1024
        pb_amount = tb_amount / 1024
        if pb_amount >= 1:
            return f"{pb_amount:.2f} PB"
        if tb_amount >= 1:
            return f"{tb_amount:.2f} TB"
        if gb_amount >= 1:
            return f"{gb_amount:.2f} GB"
        return f"{mb_amount:.2f} MB"
