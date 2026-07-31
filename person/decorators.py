from functools import wraps

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

# Page views: redirect anonymous/non-staff users to the site's own login page
# (not admin:login, which this project doesn't use for its custom staff UI).
staff_required = staff_member_required(login_url=settings.LOGIN_URL)


def staff_api_required(view):
    """API views: a plain JSON 403 instead of a redirect, so fetch() callers get
    something they can branch on instead of following it to an HTML login page."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            return JsonResponse({'error': 'forbidden'}, status=403)
        return view(request, *args, **kwargs)
    return wrapper
