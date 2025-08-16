from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication

User = get_user_model()

class ForceAdminAuthentication(BaseAuthentication):
    """
    DRF Authentication class that always authenticates as admin if no user is authenticated.
    """
    def authenticate(self, request):
        try:
            admin_user = User.objects.get(username="admin")
        except User.DoesNotExist:
            raise Exception('Superuser "admin" not found. Please create it first.')

        return (admin_user, None)
