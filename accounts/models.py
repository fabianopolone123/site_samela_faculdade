from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField('e-mail', unique=True)
    login_name = models.CharField('login', max_length=150, unique=True, blank=True, null=True)
    full_name = models.CharField('nome completo', max_length=255, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class BudgetSection(models.Model):
    code = models.CharField('codigo', max_length=20, unique=True)
    title = models.CharField('titulo', max_length=255)
    description = models.TextField('descricao', blank=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.title}'


class BudgetProduct(models.Model):
    section = models.ForeignKey(
        BudgetSection,
        on_delete=models.CASCADE,
        related_name='products',
    )
    name = models.CharField('nome do produto', max_length=255)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def selected_quote(self):
        return self.quotes.filter(is_selected=True).first()


class BudgetQuote(models.Model):
    product = models.ForeignKey(
        BudgetProduct,
        on_delete=models.CASCADE,
        related_name='quotes',
    )
    quote_number = models.PositiveSmallIntegerField('orcamento')
    price = models.DecimalField('preco', max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField('quantidade')
    link = models.URLField('link')
    is_selected = models.BooleanField('selecionado', default=False)

    class Meta:
        ordering = ['quote_number']
        unique_together = [('product', 'quote_number')]

    def __str__(self):
        return f'{self.product.name} - orcamento {self.quote_number}'

    @property
    def total(self):
        return self.price * self.quantity


class SignupCode(models.Model):
    email = models.EmailField('e-mail')
    code = models.CharField('codigo', max_length=6)
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
