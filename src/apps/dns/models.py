from django.db import models

from config.base_model import BaseModel


class DNSRecord(BaseModel):
    domain = models.CharField(max_length=255, verbose_name='Domain')
    ip_address = models.GenericIPAddressField(verbose_name='IP Address')

    class Meta:
        verbose_name = 'DNS record'
        verbose_name_plural = 'DNS records'

    def __str__(self):
        return f'{self.domain} -> {self.ip_address}'
