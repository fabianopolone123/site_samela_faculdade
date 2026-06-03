import secrets
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import (
    BudgetCostForm,
    LoginForm,
    SignupCodeForm,
    SignupEmailForm,
    SignupPasswordForm,
)
from .models import (
    BudgetCostEntry,
    BudgetCostQuote,
    BudgetProduct,
    BudgetQuote,
    BudgetSection,
    SignupCode,
    User,
)

SIGNUP_EMAIL_SESSION_KEY = 'signup_email'
SIGNUP_STEP_SESSION_KEY = 'signup_step'
SIGNUP_CODE_SESSION_KEY = 'signup_code_id'
PROJECT_INFO = {
    'title': 'Orçamento - FAPESP - Fundação Bracell Fundação Itaú',
    'subtitle': 'Auxílio à Pesquisa para o Fortalecimento da Educação na Pré-Escola',
    'edition': '06/2026',
    'organization': 'NEEVY - UFSCar',
}
PROJECT_BUDGET_TITLE = (
    'INDICADORES E CRITÉRIOS DE AVALIAÇÃO DE DESENVOLVIMENTO CULTURAL '
    'DE CRIANÇAS DE PRÉ-ESCOLA NA THC'
)
PROJECT_BUDGET_DESCRIPTION = (
    'A FAPESP, conforme estabelecido no convênio celebrado com a Fundação Bracell '
    'e a Fundação Itaú, cobrirá os custos do projeto de pesquisa segundo normas '
    'e orientações para Auxílio à Pesquisa Regular (para projetos com teto '
    'orçamentário de R$ 600 mil) ou para Projeto Temático (sem teto orçamentário). '
    'Serão aprovadas propostas até o limite orçamentário da Chamada '
    '(total de R$ 6.400.000,00). O orçamento do projeto de pesquisa apresentado '
    'à FAPESP deverá ser detalhado e cada item justificado especificamente em '
    'termos dos objetivos do projeto proposto. Destaca-se nessa modalidade que '
    'poderão ser custeadas atividades relacionadas ao desenvolvimento da pesquisa '
    'em outros estados, incluindo trabalhos de campo, desde que o Pesquisador '
    'Responsável seja vinculado a uma Instituição Sede do Estado de São Paulo.'
)


class ProjectLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_signup_context(self.request))
        context['project_info'] = PROJECT_INFO
        return context


def login_view(request):
    return ProjectLoginView.as_view()(request)


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


@login_required
def budget_product_create_view(request):
    sections = get_cost_sections()

    if request.method == 'POST':
        form = BudgetCostForm(request.POST)
        if form.is_valid():
            section = BudgetSection.objects.get(code=form.cleaned_data['section_code'])
            entry = BudgetCostEntry.objects.create(
                section=section,
                title=form.cleaned_data['title'],
                details=form.cleaned_data.get('details', ''),
                justification=form.cleaned_data.get('justification', ''),
                quantity=form.cleaned_data.get('quantity'),
                unit=form.cleaned_data.get('unit', ''),
                selected_quote_number=(
                    int(form.cleaned_data['selected_quote'])
                    if form.cleaned_data.get('selected_quote')
                    else None
                ),
                data=build_entry_data(form.cleaned_data),
            )

            if section.code in {'a', 'b', 'c', 'd.1'}:
                for quote_number in range(1, 4):
                    BudgetCostQuote.objects.create(
                        entry=entry,
                        quote_number=quote_number,
                        amount=form.cleaned_data[f'quote_{quote_number}_amount'],
                        link=form.cleaned_data[f'quote_{quote_number}_link'],
                    )

            messages.success(request, 'Custo cadastrado com sucesso.')
            return redirect('budget_product_create')
    else:
        form = BudgetCostForm()

    entries = (
        BudgetCostEntry.objects.select_related('section')
        .prefetch_related('quotes')
        .order_by('section__code', '-created_at')
    )
    return render(
        request,
        'accounts/budget_product_form.html',
        {
            'form': form,
            'sections': sections,
            'entries': entries,
        },
    )


@login_required
def budget_ready_view(request):
    leaf_sections = get_cost_sections()
    section_blocks = []
    category_totals = {'a': Decimal('0'), 'b': Decimal('0'), 'c': Decimal('0'), 'd': Decimal('0'), 'e': Decimal('0')}

    for section in leaf_sections:
        entries = list(
            BudgetCostEntry.objects.filter(section=section)
            .prefetch_related('quotes')
            .order_by('created_at')
        )
        section_total = Decimal('0')
        for entry in entries:
            section_total += Decimal(entry.total_considered or 0)

        parent_key = section.code.split('.')[0]
        category_totals[parent_key] += section_total
        section_blocks.append(
            {
                'section': section,
                'entries': entries,
                'section_total': section_total,
            }
        )

    general_total = sum(category_totals.values(), Decimal('0'))

    return render(
        request,
        'accounts/budget_ready.html',
        {
            'project_budget_title': PROJECT_BUDGET_TITLE,
            'project_budget_description': PROJECT_BUDGET_DESCRIPTION,
            'section_blocks': section_blocks,
            'category_totals': category_totals,
            'general_total': general_total,
        },
    )


def logout_view(request):
    logout(request)
    messages.success(request, 'Sessão encerrada com sucesso.')
    return redirect('login')


def signup_email_view(request):
    if request.method != 'POST':
        return redirect('login')

    form = SignupEmailForm(request.POST)
    if not form.is_valid():
        persist_signup_state(request, step='email')
        return render_login_with_forms(request, email_form=form)

    email = normalize_email(form.cleaned_data['email'])

    if email not in settings.ALLOWED_SIGNUP_EMAILS:
        form.add_error('email', 'Este e-mail não está autorizado para cadastro.')
        persist_signup_state(request, step='email')
        return render_login_with_forms(request, email_form=form)

    if User.objects.filter(email=email).exists():
        form.add_error('email', 'Já existe uma conta criada para este e-mail.')
        persist_signup_state(request, step='email')
        return render_login_with_forms(request, email_form=form)

    signup_code = SignupCode.objects.create(
        email=email,
        code=generate_code(),
        expires_at=SignupCode.expiration_time(),
    )

    send_mail(
        subject='Seu código de acesso ao portal NEEVY - UFSCar',
        message=(
            f'Seu código de verificação é: {signup_code.code}\n\n'
            f'Validade: {settings.SIGNUP_CODE_EXPIRATION_MINUTES} minutos.\n'
            'Se você não solicitou este cadastro, ignore esta mensagem.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    persist_signup_state(
        request,
        email=email,
        step='code',
        code_id=signup_code.id,
    )
    messages.success(
        request,
        (
            f'Código enviado para {email}. '
            'Se não encontrar na caixa de entrada, verifique também Spam e Lixo eletrônico.'
        ),
    )
    return redirect('login')


def signup_code_view(request):
    if request.method != 'POST':
        return redirect('login')

    signup_code = get_active_signup_code(request)
    if signup_code is None:
        messages.error(request, 'Solicite um novo código para continuar.')
        clear_signup_state(request)
        return redirect('login')

    form = SignupCodeForm(request.POST)
    if not form.is_valid():
        persist_signup_state(request, email=signup_code.email, step='code', code_id=signup_code.id)
        return render_login_with_forms(request, code_form=form)

    submitted_code = form.cleaned_data['code'].strip()
    if submitted_code != signup_code.code:
        form.add_error('code', 'Código inválido. Verifique o e-mail informado.')
        persist_signup_state(request, email=signup_code.email, step='code', code_id=signup_code.id)
        return render_login_with_forms(request, code_form=form)

    signup_code.mark_verified()
    persist_signup_state(
        request,
        email=signup_code.email,
        step='password',
        code_id=signup_code.id,
    )
    messages.success(request, 'Código validado. Agora defina sua senha.')
    return redirect('login')


def signup_password_view(request):
    if request.method != 'POST':
        return redirect('login')

    signup_code = get_active_signup_code(request)
    if signup_code is None or signup_code.verified_at is None:
        messages.error(request, 'Valide o código antes de criar sua senha.')
        clear_signup_state(request)
        return redirect('login')

    form = SignupPasswordForm(request.POST)
    if not form.is_valid():
        persist_signup_state(request, email=signup_code.email, step='password', code_id=signup_code.id)
        return render_login_with_forms(request, password_form=form)

    user = User.objects.create_user(
        email=signup_code.email,
        login_name=signup_code.email.split('@')[0],
        password=form.cleaned_data['password1'],
    )
    signup_code.mark_consumed()

    send_mail(
        subject='Conta criada com sucesso no portal NEEVY - UFSCar',
        message=(
            'Seu cadastro foi concluído com sucesso.\n\n'
            f'E-mail de acesso: {user.email}\n'
            f'Data de criação: {timezone.localtime().strftime("%d/%m/%Y %H:%M")}\n'
            'A partir de agora você já pode fazer login no portal.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    clear_signup_state(request)
    messages.success(request, 'Conta criada com sucesso. Faça login para continuar.')
    return redirect('login')


def signup_reset_view(request):
    clear_signup_state(request)
    messages.info(request, 'Fluxo de cadastro cancelado.')
    return redirect('login')


def render_login_with_forms(request, email_form=None, code_form=None, password_form=None):
    context = build_signup_context(request)
    context.update(
        {
            'form': LoginForm(request, data=request.POST if request.path == '/' else None),
            'email_form': email_form or SignupEmailForm(),
            'code_form': code_form or SignupCodeForm(),
            'password_form': password_form or SignupPasswordForm(),
            'project_info': PROJECT_INFO,
        }
    )
    return render(request, 'accounts/login.html', context)


def build_signup_context(request):
    email = request.session.get(SIGNUP_EMAIL_SESSION_KEY, '')
    step = request.session.get(SIGNUP_STEP_SESSION_KEY, 'email')
    return {
        'email_form': SignupEmailForm(initial={'email': email}),
        'code_form': SignupCodeForm(),
        'password_form': SignupPasswordForm(),
        'signup_email': email,
        'signup_step': step,
        'signup_modal_open': (
            SIGNUP_STEP_SESSION_KEY in request.session
            or SIGNUP_EMAIL_SESSION_KEY in request.session
        ),
    }


def persist_signup_state(request, email=None, step='email', code_id=None):
    if email:
        request.session[SIGNUP_EMAIL_SESSION_KEY] = email
    request.session[SIGNUP_STEP_SESSION_KEY] = step
    if code_id:
        request.session[SIGNUP_CODE_SESSION_KEY] = code_id
    request.session.modified = True


def clear_signup_state(request):
    for key in [
        SIGNUP_EMAIL_SESSION_KEY,
        SIGNUP_STEP_SESSION_KEY,
        SIGNUP_CODE_SESSION_KEY,
    ]:
        request.session.pop(key, None)
    request.session.modified = True


def get_active_signup_code(request):
    code_id = request.session.get(SIGNUP_CODE_SESSION_KEY)
    if not code_id:
        return None

    try:
        signup_code = SignupCode.objects.get(id=code_id)
    except SignupCode.DoesNotExist:
        return None

    if not signup_code.is_available:
        return None

    return signup_code


def get_budget_section():
    return BudgetSection.objects.get(code='5.1')


def get_cost_sections():
    return list(BudgetSection.objects.filter(code__in=['a', 'b', 'c', 'd.1', 'd.2', 'e']).order_by('code'))


def build_entry_data(cleaned_data):
    return {
        'transport_mode': cleaned_data.get('transport_mode', ''),
        'origin': cleaned_data.get('origin', ''),
        'destination': cleaned_data.get('destination', ''),
        'purpose': cleaned_data.get('purpose', ''),
        'people_count': cleaned_data.get('people_count'),
        'period': cleaned_data.get('period', ''),
        'daily_type': cleaned_data.get('daily_type', ''),
        'location': cleaned_data.get('location', ''),
        'days_count': cleaned_data.get('days_count'),
        'unit_value': float(cleaned_data.get('unit_value') or 0),
        'scholarship_modality': cleaned_data.get('scholarship_modality', ''),
        'duration_months': cleaned_data.get('duration_months'),
        'monthly_value': float(cleaned_data.get('monthly_value') or 0),
        'education_level': cleaned_data.get('education_level', ''),
        'weekly_dedication': cleaned_data.get('weekly_dedication', ''),
    }


def generate_code():
    return f'{secrets.randbelow(1000000):06d}'


def normalize_email(email):
    return email.strip().lower()
