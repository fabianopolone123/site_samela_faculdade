from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    BudgetCostEntry,
    BudgetCostQuote,
    BudgetProduct,
    BudgetQuote,
    BudgetSection,
    SignupCode,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'login_name', 'full_name', 'is_staff', 'is_active')
    search_fields = ('email', 'login_name', 'full_name')
    fieldsets = (
        (None, {'fields': ('email', 'login_name', 'password')}),
        ('Informacoes pessoais', {'fields': ('full_name',)}),
        ('Permissoes', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'login_name', 'password1', 'password2'),
            },
        ),
    )


@admin.register(SignupCode)
class SignupCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'expires_at', 'verified_at', 'consumed_at')
    search_fields = ('email', 'code')


@admin.register(BudgetSection)
class BudgetSectionAdmin(admin.ModelAdmin):
    list_display = ('code', 'title')
    search_fields = ('code', 'title')


class BudgetQuoteInline(admin.TabularInline):
    model = BudgetQuote
    extra = 0


@admin.register(BudgetProduct)
class BudgetProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'created_at')
    list_filter = ('section',)
    search_fields = ('name',)
    inlines = [BudgetQuoteInline]


class BudgetCostQuoteInline(admin.TabularInline):
    model = BudgetCostQuote
    extra = 0


@admin.register(BudgetCostEntry)
class BudgetCostEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'quantity', 'selected_quote_number', 'created_at')
    list_filter = ('section',)
    search_fields = ('title', 'details', 'justification')
    inlines = [BudgetCostQuoteInline]
