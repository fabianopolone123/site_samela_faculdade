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
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.title}'

    @property
    def is_leaf(self):
        return not self.children.exists()


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


class BudgetCostEntry(models.Model):
    section = models.ForeignKey(
        BudgetSection,
        on_delete=models.CASCADE,
        related_name='cost_entries',
    )
    title = models.CharField('titulo', max_length=255)
    details = models.TextField('detalhes', blank=True)
    justification = models.TextField('justificativa', blank=True)
    quantity = models.PositiveIntegerField('quantidade', null=True, blank=True)
    unit = models.CharField('unidade', max_length=100, blank=True)
    selected_quote_number = models.PositiveSmallIntegerField('orcamento selecionado', null=True, blank=True)
    data = models.JSONField('dados extras', default=dict, blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['section__code', 'created_at']

    def __str__(self):
        return f'{self.section.code} - {self.title}'

    @property
    def selected_quote(self):
        if not self.selected_quote_number:
            return None
        return self.quotes.filter(quote_number=self.selected_quote_number).first()

    @property
    def total_considered(self):
        code = self.section.code
        if code in ['a', 'b', 'c', 'd.1']:
            quote = self.selected_quote
            if not quote:
                return 0
            quantity = self.quantity or 1
            return quote.amount * quantity
        if code == 'd.2':
            people_count = self.data.get('people_count', 0) or 0
            days_count = self.data.get('days_count', 0) or 0
            unit_value = self.data.get('unit_value', 0) or 0
            return people_count * days_count * unit_value
        if code == 'e':
            quantity = self.quantity or 0
            duration_months = self.data.get('duration_months', 0) or 0
            monthly_value = self.data.get('monthly_value', 0) or 0
            if self.data.get('scholarship_modality') == 'Participação em Curso':
                return quantity * monthly_value
            return quantity * duration_months * monthly_value
        return 0


class BudgetCostQuote(models.Model):
    entry = models.ForeignKey(
        BudgetCostEntry,
        on_delete=models.CASCADE,
        related_name='quotes',
    )
    quote_number = models.PositiveSmallIntegerField('orcamento')
    amount = models.DecimalField('valor', max_digits=12, decimal_places=2)
    link = models.URLField('link')

    class Meta:
        ordering = ['quote_number']
        unique_together = [('entry', 'quote_number')]

    def __str__(self):
        return f'{self.entry.title} - orçamento {self.quote_number}'


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
