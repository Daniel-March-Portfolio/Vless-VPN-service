from django.contrib import admin

from apps.traffic.models import TrafficUsage


@admin.register(TrafficUsage)
class TrafficUsageAdmin(admin.ModelAdmin):
    list_display = ('id', 'server_id', 'upload_mb', 'download_mb', 'total_mb', 'created_at')
    ordering = ('-created_at',)
