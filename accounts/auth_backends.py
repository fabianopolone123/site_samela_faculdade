from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import User


class EmailOrLoginNameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        login_value = (username or kwargs.get('email') or '').strip().lower()
        if not login_value or password is None:
            return None

        try:
            user = User.objects.get(
                Q(email__iexact=login_value) | Q(login_name__iexact=login_value)
            )
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
