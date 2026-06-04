from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['item', 'quantity', 'unit_price', 'amount', 'received_quantity']
    readonly_fields = ['amount', 'received_quantity']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'supplier', 'order_date', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'order_date']
    search_fields = ['order_no', 'supplier__name']
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ['order_no', 'total_amount', 'created_at', 'updated_at']


class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 1
    fields = ['order_item', 'quantity_received', 'notes']


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_no', 'purchase_order', 'receipt_date', 'status', 'created_at']
    list_filter = ['status', 'receipt_date']
    search_fields = ['receipt_no', 'purchase_order__order_no']
    inlines = [GoodsReceiptItemInline]
    readonly_fields = ['receipt_no', 'created_at']
