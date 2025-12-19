from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.timezone import localtime

from apps.balance.models import BalanceHistory
from apps.server.models import Server
from apps.tariff.models import Tariff
from apps.user.models import User
from config.base_model import BaseModel


class Key(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name='keys')
    servers = models.ManyToManyField(Server, verbose_name='Server', related_name='keys')
    title = models.CharField(max_length=255, verbose_name='Title')
    tariff = models.ForeignKey(Tariff, on_delete=models.PROTECT, verbose_name='Tariff')
    end_date = models.DateTimeField(verbose_name='Expiration Date')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    auto_renew = models.BooleanField(default=True, verbose_name='Auto Renew')

    class Meta:
        verbose_name = 'Key'
        verbose_name_plural = 'Keys'

    @property
    def used_traffic_percentage(self) -> float:
        allocated_traffic = self.tariff.traffic
        traffic = self.traffic.filter(created_at__gt=self.end_date - relativedelta(days=settings.MONTH_DAYS))
        used_traffic = traffic.aggregate(total_mb=Sum('total_mb'))['total_mb'] or 0
        if allocated_traffic == 0:
            return 0.0
        return min(100, round((used_traffic / allocated_traffic) * 100, 2))

    @property
    def used_traffic_display(self) -> str:
        traffic = self.traffic.filter(created_at__gt=self.end_date - relativedelta(days=settings.MONTH_DAYS))
        used_traffic = traffic.aggregate(total_mb=Sum('total_mb'))['total_mb'] or 0
        used_mb = used_traffic
        used_gb = used_traffic / 1024
        if used_gb >= 1:
            return f"{used_gb:.2f} GB"
        return f"{used_mb:.2f} MB"

    @property
    def used_traffic(self) -> int:
        traffic = self.traffic.filter(created_at__gt=self.end_date - relativedelta(days=settings.MONTH_DAYS))
        used_traffic = traffic.aggregate(total_mb=Sum('total_mb'))['total_mb'] or 0
        return used_traffic

    @property
    def is_traffic_fully_used(self) -> bool:
        allocated_traffic = self.tariff.traffic
        traffic = self.traffic.filter(created_at__gt=self.end_date - relativedelta(days=settings.MONTH_DAYS))
        used_traffic = traffic.aggregate(total_mb=Sum('total_mb'))['total_mb'] or 0
        return used_traffic >= allocated_traffic

    @property
    def app_key(self) -> str:
        return f"vless://{self.id}@{self.domain}?type=tcp&security=reality&pbk={settings.VLESS_PUBLIC_KEY}&fp=random&sni=wikipedia.org&sid={self.short_id}&spx=%2F&flow=xtls-rprx-vision#{self.title}"

    @property
    def domain(self) -> str:
        return f'{self.id}.{settings.KEYS_ROOT_DOMAIN}:{settings.VLESS_PORT}'

    @property
    def short_id(self) -> str:
        return settings.VLESS_SHORT_IDS[self.id.int % len(settings.VLESS_SHORT_IDS)]

    def __str__(self):
        return f'{self.title} ({self.user.username})'

    def refuel(self, description: str) -> None:
        if self.used_traffic >= self.tariff.traffic or not self.is_active:
            if self.user.balance >= self.tariff.price:
                BalanceHistory(
                    user=self.user,
                    amount=-self.tariff.price,
                    description=description,
                ).save()
                self.is_active = True
                self.end_date = max(localtime(), self.end_date) + relativedelta(days=settings.MONTH_DAYS)
                self.save()
                KeyExpNotifications.objects.filter(key=self).delete()
            else:
                raise ValueError('Insufficient balance to refuel the key')
        else:
            raise ValueError('Key is already active and has remaining traffic')


class KeyTraffic(BaseModel):
    key = models.ForeignKey(Key, on_delete=models.CASCADE, verbose_name='Key', related_name='traffic')
    upload_mb = models.PositiveBigIntegerField(default=0, verbose_name='Uploaded (MB)')
    download_mb = models.PositiveBigIntegerField(default=0, verbose_name='Downloaded (MB)')
    total_mb = models.PositiveBigIntegerField(default=0, verbose_name='Total (MB)')

    class Meta:
        verbose_name = 'Key Traffic'
        verbose_name_plural = 'Key Traffics'


class KeyExpNotifications(BaseModel):
    key = models.OneToOneField(Key, on_delete=models.CASCADE, verbose_name='Key', related_name='exp_notification')
    notified_at = models.DateTimeField(verbose_name='Notified At')

    class Meta:
        verbose_name = 'Key Expiration Notification'
        verbose_name_plural = 'Key Expiration Notifications'
