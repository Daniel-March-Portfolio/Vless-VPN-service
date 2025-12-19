from django.contrib import admin

from apps.tariff.models import Tariff

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at', 'updated_at')