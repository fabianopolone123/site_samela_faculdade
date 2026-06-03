from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField('e-mail', unique=True)
    full_name = models.CharField('nome completo', max_length=255, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class SignupCode(models.Model):
    email = models.EmailField('e-mail')
    code = models.CharField('código', max_length=6)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    expires_at = models.DateTimeField('expira em')
    verified_at = models.DateTimeField('verificado em', null=True, blank=True)
    consumed_at = models.DateTimeField('consumido em', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def mark_verified(self):
        self.verified_at = timezone.now()
        self.save(update_fields=['verified_at'])

    def mark_consumed(self):
        self.consumed_at = timezone.now()
        self.save(update_fields=['consumed_at'])

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_available(self):
        return not self.is_expired and self.consumed_at is None

    @classmethod
    def expiration_time(cls):
        return timezone.now() + timedelta(
            minutes=settings.SIGNUP_CODE_EXPIRATION_MINUTES
        )
