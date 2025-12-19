from django.contrib import admin

from apps.key.models import Key, KeyTraffic, KeyExpNotifications


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_display = ('id', 'user', 'title', 'created_at')
    search_fields = ('user__username', )
    ordering = ('-created_at',)

@admin.register(KeyTraffic)
class KeyTrafficAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_display = ('id', 'key', 'upload_mb', 'download_mb', 'total_mb', 'created_at')
    search_fields = ('key__user__username', )
    ordering = ('-created_at',)


@admin.register(KeyExpNotifications)
class KeyExpNotificationsAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_display = ('id', 'key', 'notified_at', 'created_at')
    search_fields = ('key__user__username', )
    ordering = ('-created_at',)