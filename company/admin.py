from django.contrib import admin

from company.models import Company, CompanyPhoto


class CompanyPhotoInline(admin.TabularInline):
    model = CompanyPhoto
    extra = 0
    fields = ('image', 'category', 'description')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('legal_name', 'country', 'verified_seller', 'created')
    list_filter = ('verified_seller', 'country')
    search_fields = ('legal_name', 'name', 'contact_email')
    inlines = [CompanyPhotoInline]
