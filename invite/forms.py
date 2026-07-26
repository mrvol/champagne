from django import forms

from company.models import Company
from goods.models import Good

FIELD_CSS = 'w-full border border-stone-300 rounded-md p-2 text-sm'


class CommaSeparatedListField(forms.CharField):
    """Renders a Company/Good JSONField(list) as a plain comma-separated text input."""

    def prepare_value(self, value):
        return ', '.join(value) if isinstance(value, list) else (value or '')

    def to_python(self, value):
        if not value:
            return []
        return [v.strip() for v in value.split(',') if v.strip()]


def style_widgets(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs.setdefault('class', 'rounded border-stone-300')
        else:
            field.widget.attrs.setdefault('class', FIELD_CSS)


class CompanyOnboardingForm(forms.ModelForm):
    founders = CommaSeparatedListField(required=False, help_text='Comma-separated names')
    certifications = CommaSeparatedListField(required=False, help_text='Comma-separated, e.g. Organic, AOC Champagne, HVE3')
    awards = CommaSeparatedListField(required=False, help_text='Comma-separated')
    languages_spoken = CommaSeparatedListField(required=False, help_text='Comma-separated, e.g. English, French')
    instagram_url = forms.URLField(required=False, label='Instagram')
    facebook_url = forms.URLField(required=False, label='Facebook')
    x_url = forms.URLField(required=False, label='X / Twitter')

    COMPANY_INFO_FIELDS = [
        'name', 'legal_name', 'vat_number', 'registration_number', 'tax_id',
        'founded_date', 'founders', 'ownership_info', 'description', 'story',
        'history', 'annual_production', 'certifications', 'awards', 'languages_spoken',
    ]
    CONTACT_FIELDS = ['contact_name', 'contact_position', 'contact_email', 'contact_phone', 'website', 'support_contact']
    ADDRESS_FIELDS = ['registered_address', 'operational_address', 'country', 'region', 'city', 'postal_code', 'latitude', 'longitude']
    BANKING_FIELDS = ['bank_name', 'bank_account_holder', 'iban', 'swift_bic', 'bank_account_number', 'payment_terms', 'currency']
    PROFILE_FIELDS = ['logo_url', 'tagline', 'instagram_url', 'facebook_url', 'x_url', 'pr_website', 'press_kit_url', 'sustainability_info']

    class Meta:
        model = Company
        fields = [
            'name', 'legal_name', 'vat_number', 'registration_number', 'tax_id',
            'founded_date', 'founders', 'ownership_info', 'description', 'story',
            'history', 'annual_production', 'certifications', 'awards', 'languages_spoken',
            'contact_name', 'contact_position', 'contact_email', 'contact_phone', 'website', 'support_contact',
            'registered_address', 'operational_address', 'country', 'region', 'city', 'postal_code', 'latitude', 'longitude',
            'bank_name', 'bank_account_holder', 'iban', 'swift_bic', 'bank_account_number', 'payment_terms', 'currency',
            'logo_url', 'tagline', 'pr_website', 'press_kit_url', 'sustainability_info',
        ]
        labels = {
            'description': 'Company description',
            'story': 'Brand story',
            'history': 'Winery history',
            'annual_production': 'Production capacity (bottles/year)',
            'tagline': 'Marketing tagline',
        }
        widgets = {
            'founded_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'story': forms.Textarea(attrs={'rows': 3}),
            'history': forms.Textarea(attrs={'rows': 3}),
            'ownership_info': forms.Textarea(attrs={'rows': 2}),
            'registered_address': forms.Textarea(attrs={'rows': 2}),
            'operational_address': forms.Textarea(attrs={'rows': 2}),
            'sustainability_info': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            social = self.instance.social_links or {}
            self.fields['instagram_url'].initial = social.get('instagram', '')
            self.fields['facebook_url'].initial = social.get('facebook', '')
            self.fields['x_url'].initial = social.get('x', '')
        style_widgets(self)

    def company_info(self):
        return [self[name] for name in self.COMPANY_INFO_FIELDS]

    def contact_info(self):
        return [self[name] for name in self.CONTACT_FIELDS]

    def address_info(self):
        return [self[name] for name in self.ADDRESS_FIELDS]

    def banking_info(self):
        return [self[name] for name in self.BANKING_FIELDS]

    def profile_info(self):
        return [self[name] for name in self.PROFILE_FIELDS]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.social_links = {k: v for k, v in {
            'instagram': self.cleaned_data.get('instagram_url'),
            'facebook': self.cleaned_data.get('facebook_url'),
            'x': self.cleaned_data.get('x_url'),
        }.items() if v}
        if commit:
            instance.save()
        return instance


class GoodOnboardingForm(forms.ModelForm):
    awards = CommaSeparatedListField(required=False, help_text='Comma-separated')

    class Meta:
        model = Good
        fields = [
            'name', 'vintage_year', 'wine_type', 'grape_variety', 'region', 'abv',
            'volume_ml', 'description', 'food_pairing', 'awards', 'available_quantity',
            'min_order_quantity', 'price', 'currency', 'stock_status',
        ]
        labels = {
            'description': 'Tasting notes',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'food_pairing': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_widgets(self)
