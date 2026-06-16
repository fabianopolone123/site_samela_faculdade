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
    code = models.CharField('código', max_length=20, unique=True)
    title = models.CharField('título', max_length=255)
    description = models.TextField('descrição', blank=True)
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
    quote_number = models.PositiveSmallIntegerField('orçamento')
    price = models.DecimalField('preço', max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField('quantidade')
    link = models.URLField('link')
    is_selected = models.BooleanField('selecionado', default=False)

    class Meta:
        ordering = ['quote_number']
        unique_together = [('product', 'quote_number')]

    def __str__(self):
        return f'{self.product.name} - orçamento {self.quote_number}'

    @property
    def total(self):
        return self.price * self.quantity


class BudgetCostEntry(models.Model):
    section = models.ForeignKey(
        BudgetSection,
        on_delete=models.CASCADE,
        related_name='cost_entries',
    )
    title = models.CharField('título', max_length=255)
    details = models.TextField('detalhes', blank=True)
    justification = models.TextField('justificativa', blank=True)
    quantity = models.PositiveIntegerField('quantidade', null=True, blank=True)
    unit = models.CharField('unidade', max_length=100, blank=True)
    selected_quote_number = models.PositiveSmallIntegerField(
        'orçamento selecionado',
        null=True,
        blank=True,
    )
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
            if code == 'a':
                return quote.total_with_freight
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
    quote_number = models.PositiveSmallIntegerField('orçamento')
    amount = models.DecimalField('valor', max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField('quantidade', null=True, blank=True)
    freight = models.DecimalField('frete', max_digits=12, decimal_places=2, null=True, blank=True)
    link = models.URLField('link')

    class Meta:
        ordering = ['quote_number']
        unique_together = [('entry', 'quote_number')]

    def __str__(self):
        return f'{self.entry.title} - orçamento {self.quote_number}'

    @property
    def total_with_freight(self):
        quantity = self.quantity or 0
        freight = self.freight or 0
        return (self.amount * quantity) + freight


class CostTopic(models.Model):
    name = models.CharField('nome', max_length=255)
    description = models.TextField('descrição', blank=True, default='')
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CostField(models.Model):
    TYPE_TEXT = 'texto'
    TYPE_NUMBER = 'numero'
    TYPE_LINK = 'link'
    TYPE_CURRENCY = 'valor'
    ROLE_NONE = 'nenhuma'
    ROLE_UNIT_PRICE = 'preco_unitario'
    ROLE_MULTIPLIER = 'multiplicador'
    ROLE_FREIGHT = 'frete'
    ROLE_SELECTOR = 'orcamento_selecionado'
    ROLE_CALCULATED_TOTAL = 'total_calculado'
    TYPE_CHOICES = [
        (TYPE_TEXT, 'Texto'),
        (TYPE_NUMBER, 'Número'),
        (TYPE_LINK, 'Link'),
        (TYPE_CURRENCY, 'Valor'),
    ]
    CALCULATION_ROLE_CHOICES = [
        (ROLE_NONE, 'Sem função'),
        (ROLE_UNIT_PRICE, 'Preço unitário'),
        (ROLE_MULTIPLIER, 'Multiplicador / Quantidade'),
        (ROLE_FREIGHT, 'Frete / Adicional'),
        (ROLE_SELECTOR, 'Seletor de orçamento'),
        (ROLE_CALCULATED_TOTAL, 'Total calculado'),
    ]

    topic = models.ForeignKey(
        CostTopic,
        on_delete=models.CASCADE,
        related_name='fields',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )
    name = models.CharField('nome', max_length=255)
    field_type = models.CharField('tipo', max_length=20, choices=TYPE_CHOICES)
    calculation_role = models.CharField(
        'função de cálculo',
        max_length=30,
        choices=CALCULATION_ROLE_CHOICES,
        default=ROLE_NONE,
    )
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name


class CostRecord(models.Model):
    topic = models.ForeignKey(
        CostTopic,
        on_delete=models.CASCADE,
        related_name='records',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class CostRecordValue(models.Model):
    record = models.ForeignKey(
        CostRecord,
        on_delete=models.CASCADE,
        related_name='values',
    )
    field = models.ForeignKey(
        CostField,
        on_delete=models.CASCADE,
        related_name='record_values',
    )
    value = models.TextField('valor', blank=True)

    class Meta:
        unique_together = [('record', 'field')]


class AuditLog(models.Model):
    ACTION_CREATE = 'cadastro'
    ACTION_UPDATE = 'alteracao'
    ACTION_DELETE = 'exclusao'
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Cadastro'),
        (ACTION_UPDATE, 'Alteração'),
        (ACTION_DELETE, 'Exclusão'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField('ação', max_length=20, choices=ACTION_CHOICES)
    target_type = models.CharField('tipo do registro', max_length=100)
    target_name = models.CharField('registro', max_length=255)
    description = models.TextField('detalhes', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_action_display()} - {self.target_type}: {self.target_name}'


class AllowedSignupEmail(models.Model):
    email = models.EmailField('e-mail', unique=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['email']

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
