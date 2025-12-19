from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from config.base_model import BaseModel


class Server(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Title')
    ip_address = models.GenericIPAddressField(verbose_name='IP address')
    location = models.CharField(max_length=255, verbose_name='Location', blank=True, null=True)

    api_url = models.URLField(verbose_name='API URL')
    api_user = models.CharField(max_length=255, verbose_name='API user')
    api_key = models.CharField(max_length=255, verbose_name='API key')

    do_setup = models.BooleanField(default=True, verbose_name='Needs Setup. (All inbounds will be deleted and recreated)')

    class Meta:
        verbose_name = 'Server'
        verbose_name_plural = 'Servers'

    def __str__(self):
        return f'{self.name}'


@receiver(post_save, sender=Server)
def server_post_save_handler(sender, instance: Server, created: bool, **kwargs) -> None:
    if instance.do_setup:
        from apps.server.services import SetupServerService
        SetupServerService().setup(instance.id)
        if instance.do_setup:
            instance.do_setup = False
            instance.save(update_fields=['do_setup'])
