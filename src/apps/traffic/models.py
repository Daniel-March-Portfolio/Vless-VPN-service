from django.db import models

from apps.server.models import Server
from apps.user.models import User
from config.base_model import BaseModel


class TrafficUsage(BaseModel):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, verbose_name='Server', related_name='+')
    key_id = models.UUIDField(verbose_name='Key ID')
    upload_mb = models.PositiveBigIntegerField(default=0, verbose_name='Upload (MB')
    download_mb = models.PositiveBigIntegerField(default=0, verbose_name='Download (MB)')
    total_mb = models.PositiveBigIntegerField(default=0, verbose_name='Total (MB)')

    class Meta:
        verbose_name = 'Traffic Usage'
        verbose_name_plural = 'Traffic Usages'

        indexes = [
            models.Index(fields=['key_id', 'server']),
        ]
