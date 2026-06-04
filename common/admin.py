from django.contrib import admin
from .models import Supplier, Item


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_person', 'phone', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'unit', 'standard_price', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['code', 'name']
