from django.contrib import admin

from apps.balance.models import BalanceHistory


@admin.register(BalanceHistory)
class BalanceHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at', 'updated_at')
    list_display = ('id', 'user', 'amount', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)
