from django.utils.translation import gettext_lazy as _

from company.models import Company
from goods.models import Good
from invite.models import Invitation

# To add a new staff section, append a section (or an item to an existing one) here —
# base.html renders this generically. `icon` must match one of the cases in base.html's
# sidebar icon block. `count` is optional decoration, filled in below for staff users.
# Labels use gettext_lazy, not gettext: this list is built once at import time, so an
# eager translation would freeze on whatever locale was active on first import.
STAFF_NAV_SECTIONS = [
    {
        'label': None,
        'items': [
            {'url_name': 'staff_dashboard', 'label': _('Overview'), 'icon': 'chart', 'count': None},
        ],
    },
    {
        'label': _('Catalog'),
        'items': [
            {'url_name': 'staff_good_list', 'label': _('Products'), 'icon': 'grid', 'count': None},
            {'url_name': 'staff_company_list', 'label': _('Companies'), 'icon': 'building', 'count': None},
            {'url_name': 'staff_invite_list', 'label': _('Invitations'), 'icon': 'mail', 'count': None},
        ],
    },
    {
        'label': _('Sales'),
        'items': [
            {'url_name': 'staff_order_list', 'label': _('Orders'), 'icon': 'receipt', 'count': None},
            {'url_name': 'staff_user_list', 'label': _('Customers'), 'icon': 'user', 'count': None},
        ],
    },
]

_COUNTS = {
    'staff_good_list': lambda: Good.objects.filter(company__verified_seller=True).count(),
    'staff_company_list': lambda: Company.objects.count(),
    'staff_invite_list': lambda: Invitation.objects.filter(
        status__in=[Invitation.STATUS_PENDING, Invitation.STATUS_IN_PROGRESS]).count(),
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
