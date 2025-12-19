from django.contrib import admin

from apps.dns.models import DNSRecord


@admin.register(DNSRecord)
class DNSRecordAdmin(admin.ModelAdmin):
    list_display = ('domain', 'ip_address', 'created_at', 'updated_at')
    search_fields = ('domain', 'ip_address')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at')

