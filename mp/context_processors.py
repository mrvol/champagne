from company.models import Company
from goods.models import Good

# To add a new staff section, append a section (or an item to an existing one) here —
# base.html renders this generically. `icon` must match one of the cases in base.html's
# sidebar icon block. `count` is optional decoration, filled in below for staff users.
STAFF_NAV_SECTIONS = [
    {
        'label': None,
        'items': [
            {'url_name': 'staff_dashboard', 'label': 'Overview', 'icon': 'chart', 'count': None},
        ],
    },
    {
        'label': 'Catalog',
        'items': [
            {'url_name': 'staff_good_list', 'label': 'Products', 'icon': 'grid', 'count': None},
            {'url_name': 'staff_company_list', 'label': 'Companies', 'icon': 'building', 'count': None},
        ],
    },
    {
        'label': 'Sales',
        'items': [
            {'url_name': 'staff_order_list', 'label': 'Orders', 'icon': 'receipt', 'count': None},
            {'url_name': 'staff_user_list', 'label': 'Customers', 'icon': 'user', 'count': None},
        ],
    },
]

_COUNTS = {
    'staff_good_list': lambda: Good.objects.filter(company__verified_seller=True).count(),
    'staff_company_list': lambda: Company.objects.count(),
}


def staff_nav(request):
    if not (request.user.is_authenticated and request.user.is_staff):
        return {'staff_nav_sections': STAFF_NAV_SECTIONS}

    sections = []
    for section in STAFF_NAV_SECTIONS:
        items = [dict(item) for item in section['items']]
        for item in items:
            if item['url_name'] in _COUNTS:
                item['count'] = _COUNTS[item['url_name']]()
        sections.append({'label': section['label'], 'items': items})
    return {'staff_nav_sections': sections}
