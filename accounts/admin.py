from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    AuditLog,
    BudgetCostEntry,
    BudgetCostQuote,
    BudgetProduct,
    BudgetQuote,
    BudgetSection,
    CostField,
    CostRecord,
    CostRecordValue,
    CostTopic,
    SignupCode,
    User,
)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'action', 'target_type', 'target_name', 'user')
    list_filter = ('action', 'target_type', 'created_at')
    search_fields = ('target_name', 'description', 'user__email', 'user__login_name')
    readonly_fields = ('user', 'action', 'target_type', 'target_name', 'description', 'created_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'login_name', 'full_name', 'is_staff', 'is_active')
    search_fields = ('email', 'login_name', 'full_name')
    fieldsets = (
        (None, {'fields': ('email', 'login_name', 'password')}),
        ('Informações pessoais', {'fields': ('full_name',)}),
        (
            'Permissões',
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')},
        ),
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
    list_display = ('code', 'title', 'parent')
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


class CostFieldInline(admin.TabularInline):
    model = CostField
    extra = 0
    fields = ('name', 'field_type', 'parent')


@admin.register(CostTopic)
class CostTopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = [CostFieldInline]


@admin.register(CostField)
class CostFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'topic', 'field_type', 'parent', 'created_at')
    list_filter = ('topic', 'field_type')
    search_fields = ('name',)


class CostRecordValueInline(admin.TabularInline):
    model = CostRecordValue
    extra = 0


@admin.register(CostRecord)
class CostRecordAdmin(admin.ModelAdmin):
    list_display = ('topic', 'created_at')
    list_filter = ('topic',)
    inlines = [CostRecordValueInline]
