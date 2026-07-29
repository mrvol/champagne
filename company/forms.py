from django import forms

from company.models import Company

COMPANY_FIELDS = [
    'legal_name', 'tagline', 'story', 'region', 'industry', 'founded_date',
    'annual_production', 'contact_email', 'contact_phone', 'website',
]


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = COMPANY_FIELDS
