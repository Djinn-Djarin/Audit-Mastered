# scraping/authentication.py
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication

User = get_user_model()

class ForceAdminAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            admin_user = User.objects.get(username="admin")  # synchronous
        except User.DoesNotExist:
            raise Exception('Superuser "admin" not found. Please create it first.')
        return (admin_user, None)
