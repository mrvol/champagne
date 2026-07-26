from django.contrib import admin

from goods.models import Good


@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'vintage_year', 'wine_type', 'stock_status', 'price', 'currency')
    list_filter = ('wine_type', 'stock_status', 'company')
    search_fields = ('name', 'sku')
