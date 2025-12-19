from django.contrib import admin

from apps.telegram.models import TelegramPayment


@admin.register(TelegramPayment)
class TelegramPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'get_paid', 'cancelled', 'created_at')
    list_filter = ('cancelled',)
    search_fields = ('user__username', 'transaction_id')
    actions = ['mark_as_do_cancel']

    def get_readonly_fields(self, request, obj: TelegramPayment = None):
        readonly_fields = ['id', 'transaction_id', 'user', 'amount', 'message_id', 'cancelled', 'created_at', 'updated_at']
        if not obj or obj.cancelled or obj.do_cancel or not obj.transaction_id:
            readonly_fields.append('do_cancel')
        return readonly_fields

    @admin.display(boolean=True, description="Paid")
    def get_paid(self, obj: TelegramPayment):
        return bool(obj.transaction_id)

    def has_add_permission(self, request):
        return False


    def mark_as_do_cancel(self, request, queryset):
        updated_count = queryset.update(do_cancel=True)
        self.message_user(request, f"{updated_count} payments marked for cancel.")
    mark_as_do_cancel.short_description = "Mark selected payments for cancel"