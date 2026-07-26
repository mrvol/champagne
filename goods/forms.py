from django import forms

from goods.models import Good

GOOD_FIELDS = [
    'name', 'sku', 'description', 'vintage_year', 'region', 'grape_variety',
    'wine_type', 'sugar_level', 'price', 'currency', 'volume_ml', 'abv',
    'stock_status', 'available_quantity', 'min_order_quantity', 'organic_certified', 'barcode',
]


class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = GOOD_FIELDS
