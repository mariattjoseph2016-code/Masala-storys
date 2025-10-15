from django.contrib import admin

from .models import StockItem


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("variant", "quantity_available", "updated_at")
    search_fields = ("variant__sku", "variant__product__name")

# Register your models here.
