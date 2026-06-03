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
    BudgetProductForm,
    LoginForm,
    SignupCodeForm,
    SignupEmailForm,
    SignupPasswordForm,
)
from .models import BudgetProduct, BudgetQuote, BudgetSection, SignupCode, User

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
    return render(
        request,
        'accounts/dashboard.html',
        {
            'budget_section': get_budget_section(),
            'project_budget_title': PROJECT_BUDGET_TITLE,
        },
    )


@login_required
def budget_product_create_view(request):
    section = get_budget_section()

    if request.method == 'POST':
        form = BudgetProductForm(request.POST)
        if form.is_valid():
            product = BudgetProduct.objects.create(
                section=section,
                name=form.cleaned_data['name'],
            )
            selected_quote = int(form.cleaned_data['selected_quote'])

            for quote_number in range(1, 4):
                BudgetQuote.objects.create(
                    product=product,
                    quote_number=quote_number,
                    price=form.cleaned_data[f'quote_{quote_number}_price'],
                    quantity=form.cleaned_data[f'quote_{quote_number}_quantity'],
                    link=form.cleaned_data[f'quote_{quote_number}_link'],
                    is_selected=selected_quote == quote_number,
                )

            messages.success(request, 'Produto cadastrado com sucesso no tópico 5.1.')
            return redirect('budget_product_create')
    else:
        form = BudgetProductForm()

    products = (
        BudgetProduct.objects.filter(section=section)
        .prefetch_related('quotes')
        .order_by('-created_at')
    )
    return render(
        request,
        'accounts/budget_product_form.html',
        {
            'form': form,
            'budget_section': section,
            'products': products,
        },
    )


@login_required
def budget_ready_view(request):
    section = (
        BudgetSection.objects.prefetch_related(
            Prefetch(
                'products',
                queryset=BudgetProduct.objects.prefetch_related('quotes').order_by('-created_at'),
            )
        )
        .get(code='5.1')
    )
    selected_total = Decimal('0')
    products = []

    for product in section.products.all():
        selected_quote = product.selected_quote
        if selected_quote:
            selected_total += selected_quote.total
        products.append(
            {
                'product': product,
                'selected_quote': selected_quote,
                'quotes': product.quotes.all(),
            }
        )

    return render(
        request,
        'accounts/budget_ready.html',
        {
            'budget_section': section,
            'project_budget_title': PROJECT_BUDGET_TITLE,
            'project_budget_description': PROJECT_BUDGET_DESCRIPTION,
            'products': products,
            'selected_total': selected_total,
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


def generate_code():
    return f'{secrets.randbelow(1000000):06d}'


def normalize_email(email):
    return email.strip().lower()
