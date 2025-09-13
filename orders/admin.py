from django.contrib import admin
from .models import Order, OrderItem, OrderCancelItem


class ReadOnlyOrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    show_change_link = False
    
    fields = ['product', 'price', 'quantity', 'get_total_cost']
    readonly_fields = fields  

    def has_add_permission(self, request, obj=None):
        return False  

    def has_change_permission(self, request, obj=None):
        return False 

    def get_total_cost(self, obj):
        try:
            return "${:,.2f}".format(obj.get_cost())
        except (TypeError, AttributeError):
            return "—"
    get_total_cost.short_description = "Total"


class ReadOnlyOrderCancelItemInline(admin.TabularInline):
    model = OrderCancelItem
    extra = 0
    can_delete = False
    show_change_link = False

    fields = ['product', 'price', 'quantity', 'get_total_cost']
    readonly_fields = fields  

    def has_add_permission(self, request, obj=None):
        return False  

    def has_change_permission(self, request, obj=None):
        return False 

    def get_total_cost(self, obj):
        try:
            return "${:,.2f}".format(obj.get_cost())
        except (TypeError, AttributeError):
            return "—"
    get_total_cost.short_description = "Total (Cancelado)"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created', 'paid', 'status', 'total_amount', 'donot_show']
    list_filter = ['paid', 'status', 'created']
    search_fields = ['id', 'user__code', 'user__first_name', 'user__last_name']
    ordering = ['-created']

    fieldsets = (
        ('Información del pedido', {
            'fields': (
                'id',
                'user',
                'created',
                'arrival_time',
                'school_address', 
                'status',
                'paid',
                'total_amount',
                'qr_code_data',
            )
        }),
    )

    readonly_fields = ['id', 'created', 'total_amount', 'user', 'school_address', 'qr_code_data']

    inlines = [ReadOnlyOrderItemInline, ReadOnlyOrderCancelItemInline]

    def total_amount(self, obj):
        try:
            return "${:,.2f}".format(obj.get_total_cost())
        except (TypeError, AttributeError):
            return "—"
    total_amount.short_description = 'Total de la orden'
