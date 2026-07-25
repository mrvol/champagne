from django.conf import settings


class UserLanguageMiddleware:
    """Applies the user's saved ui_language as the effective language on visits
    where the browser hasn't explicitly chosen one yet (no language cookie)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            settings.LANGUAGE_COOKIE_NAME not in request.COOKIES
            and request.user.is_authenticated
            and request.user.ui_language
        ):
            request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = request.user.ui_language
        return self.get_response(request)
