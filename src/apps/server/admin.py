from django.contrib import admin

from apps.server.models import Server


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_display = ('id', 'name', 'ip_address', )
    search_fields = ('name', 'ip_address')
    ordering = ('name',)
