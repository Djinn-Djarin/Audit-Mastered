# scraping/middleware.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class ForceAdminUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if isinstance(request.user, AnonymousUser):
            try:
                request.user = User.objects.get(username="admin")
            except User.DoesNotExist:
                raise Exception('Superuser "admin" not found. Please create it first.')
        return self.get_response(request)
