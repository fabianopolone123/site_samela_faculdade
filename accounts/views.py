import secrets
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    LoginForm,
    SignupCodeForm,
    SignupEmailForm,
    SignupPasswordForm,
    TopicFieldForm,
    TopicForm,
)
from .models import (
    BudgetSection,
    CostField,
    CostRecord,
    CostRecordValue,
    CostTopic,
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
    'e a Fundação Itaú, cobrirá os custos do projeto de pesquisa segundo normas e '
    'orientações para Auxílio à Pesquisa Regular (para projetos com teto orçamentário '
    'de R$ 600 mil) ou para Projeto Temático (sem teto orçamentário). Serão aprovadas '
    'propostas até o limite orçamentário da Chamada (total de R$ 6.400.000,00). '
    'O orçamento do projeto de pesquisa apresentado à FAPESP deverá ser detalhado e '
    'cada item justificado especificamente em termos dos objetivos do projeto proposto.'
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
    topics = list(
        CostTopic.objects.prefetch_related(
            'fields',
            'records__values__field',
        )
    )

    selected_topic = None
    selected_topic_id = request.GET.get('topic')
    if selected_topic_id:
        selected_topic = next(
            (topic for topic in topics if str(topic.id) == selected_topic_id),
            None,
        )
    elif topics:
        selected_topic = topics[0]

    selected_rows = build_topic_rows(selected_topic) if selected_topic else []
    selected_groups = build_topic_groups(selected_topic) if selected_topic else []
    selected_records, topic_grand_total = (
        build_record_cards(selected_topic, selected_rows) if selected_topic else ([], None)
    )

    context = {
        'topics': topics,
        'selected_topic': selected_topic,
        'topic_form': TopicForm(),
        'field_form': TopicFieldForm(topic=selected_topic),
        'selected_rows': selected_rows,
        'selected_groups': selected_groups,
        'selected_records': selected_records,
        'topic_grand_total': topic_grand_total,
    }
    return render(request, 'accounts/budget_product_form.html', context)


@login_required
def create_topic_view(request):
    if request.method != 'POST':
        return redirect('budget_product_create')

    form = TopicForm(request.POST)
    if form.is_valid():
        topic = CostTopic.objects.create(name=form.cleaned_data['name'])
        messages.success(request, 'Tópico cadastrado com sucesso.')
        return redirect(f"{reverse('budget_product_create')}?topic={topic.id}")

    messages.error(request, 'Não foi possível cadastrar o tópico.')
    return redirect('budget_product_create')


@login_required
def create_topic_field_view(request):
    if request.method != 'POST':
        return redirect('budget_product_create')

    topic = get_object_or_404(CostTopic, id=request.POST.get('topic_id'))
    form = TopicFieldForm(request.POST, topic=topic)
    if form.is_valid():
        parent = None
        parent_id = form.cleaned_data.get('parent_id')
        if parent_id:
            parent = get_object_or_404(CostField, id=parent_id, topic=topic)

        CostField.objects.create(
            topic=topic,
            parent=parent,
            name=form.cleaned_data['name'],
            field_type=form.cleaned_data['field_type'],
        )
        messages.success(request, 'Campo cadastrado com sucesso.')
    else:
        messages.error(request, 'Não foi possível cadastrar o campo.')

    return redirect(f"{reverse('budget_product_create')}?topic={topic.id}&open=campos")


@login_required
def delete_topic_field_view(request, field_id):
    if request.method != 'POST':
        return redirect('budget_product_create')

    field = get_object_or_404(CostField, id=field_id)
    topic_id = field.topic_id
    field.delete()
    messages.success(request, 'Campo excluído com sucesso.')
    return redirect(f"{reverse('budget_product_create')}?topic={topic_id}&open=campos")


@login_required
def create_topic_record_view(request):
    if request.method != 'POST':
        return redirect('budget_product_create')

    topic = get_object_or_404(CostTopic, id=request.POST.get('topic_id'))
    fields = list(topic.fields.order_by('created_at'))

    if not fields:
        messages.error(request, 'Crie ao menos um campo antes de salvar um novo custo.')
        return redirect(f"{reverse('budget_product_create')}?topic={topic.id}")

    record = CostRecord.objects.create(topic=topic)
    saved_values = 0

    for field in fields:
        value = request.POST.get(f'field_{field.id}', '').strip()
        if value:
            CostRecordValue.objects.create(record=record, field=field, value=value)
            saved_values += 1

    if saved_values == 0:
        record.delete()
        messages.error(request, 'Preencha ao menos um campo para salvar o novo custo.')
    else:
        messages.success(request, 'Novo custo cadastrado com sucesso.')

    return redirect(f"{reverse('budget_product_create')}?topic={topic.id}")


@login_required
def budget_ready_view(request):
    sections = list(
        BudgetSection.objects.prefetch_related('cost_entries__quotes').order_by('code')
    )
    section_blocks = []
    category_totals = {
        'a': Decimal('0'),
        'b': Decimal('0'),
        'c': Decimal('0'),
        'd': Decimal('0'),
        'e': Decimal('0'),
    }
    general_total = Decimal('0')

    for section in sections:
        entries = list(section.cost_entries.all())
        section_total = sum((entry.total_considered for entry in entries), Decimal('0'))
        section_blocks.append(
            {
                'section': section,
                'entries': entries,
                'section_total': section_total,
            }
        )

        if section.code in ['a', 'b', 'c', 'e']:
            category_totals[section.code] += section_total
        elif section.code.startswith('d'):
            category_totals['d'] += section_total
        general_total += section_total

    context = {
        'project_budget_title': PROJECT_BUDGET_TITLE,
        'project_budget_description': PROJECT_BUDGET_DESCRIPTION,
        'section_blocks': section_blocks,
        'category_totals': category_totals,
        'general_total': general_total,
    }
    return render(request, 'accounts/budget_ready.html', context)


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
        persist_signup_state(
            request,
            email=signup_code.email,
            step='code',
            code_id=signup_code.id,
        )
        return render_login_with_forms(request, code_form=form)

    submitted_code = form.cleaned_data['code'].strip()
    if submitted_code != signup_code.code:
        form.add_error('code', 'Código inválido. Verifique o e-mail informado.')
        persist_signup_state(
            request,
            email=signup_code.email,
            step='code',
            code_id=signup_code.id,
        )
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
        persist_signup_state(
            request,
            email=signup_code.email,
            step='password',
            code_id=signup_code.id,
        )
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


def build_topic_rows(topic):
    if topic is None:
        return []

    fields = list(topic.fields.all())
    children_map = {}
    for field in fields:
        children_map.setdefault(field.parent_id, []).append(field)

    rows = []

    def walk(field, level):
        rows.append(
            {
                'field': field,
                'level': level,
                'type_label': field.get_field_type_display(),
            }
        )
        for child in children_map.get(field.id, []):
            walk(child, level + 1)

    for root in children_map.get(None, []):
        walk(root, 0)

    return rows


def build_topic_groups(topic):
    if topic is None:
        return []

    rows = build_topic_rows(topic)
    groups = []
    current_group = None

    for row in rows:
        if row['level'] == 0:
            current_group = {
                'root': row,
                'children': [],
                'has_price_calc': False,
            }
            groups.append(current_group)
        elif current_group is not None:
            name_lower = row['field'].name.lower().strip()
            if name_lower in ('preço', 'preco', 'price'):
                field_role = 'preco'
                current_group['has_price_calc'] = True
            elif name_lower == 'frete':
                field_role = 'frete'
                current_group['has_price_calc'] = True
            else:
                field_role = None
            current_group['children'].append({**row, 'field_role': field_role})

    return groups


def get_selected_total_for_record(record, topic_fields):
    values_map = {rv.field_id: rv.value for rv in record.values.all()}

    selector = next(
        (f for f in topic_fields if f.parent_id is None and 'selecionar' in f.name.lower()),
        None,
    )
    if not selector:
        return None

    selected_str = values_map.get(selector.id, '').strip()
    if not selected_str:
        return None

    orc_parent = next(
        (
            f for f in topic_fields
            if f.parent_id is None and f.name.strip() == f'Orçamento {selected_str}'
        ),
        None,
    )
    if not orc_parent:
        return None

    preco_val = Decimal('0')
    frete_val = Decimal('0')

    for f in topic_fields:
        if f.parent_id != orc_parent.id:
            continue
        val_str = values_map.get(f.id, '').strip()
        if not val_str:
            continue
        try:
            amount = Decimal(val_str)
        except (InvalidOperation, ValueError):
            continue
        name_lower = f.name.lower().strip()
        if name_lower in ('preço', 'preco'):
            preco_val = amount
        elif name_lower == 'frete':
            frete_val = amount

    return preco_val + frete_val


def build_record_cards(topic, selected_rows):
    field_order = {row['field'].id: index for index, row in enumerate(selected_rows)}
    all_fields = list(topic.fields.all())
    records = []
    grand_total = Decimal('0')
    has_totals = False

    for record in topic.records.all():
        values = sorted(
            [
                {
                    'field_name': value.field.name,
                    'field_type': value.field.get_field_type_display(),
                    'value': value.value,
                    'level': get_field_level(value.field),
                    'order': field_order.get(value.field_id, 9999),
                }
                for value in record.values.all()
            ],
            key=lambda item: item['order'],
        )
        selected_total = get_selected_total_for_record(record, all_fields)
        if selected_total is not None:
            grand_total += selected_total
            has_totals = True
        records.append({'record': record, 'values': values, 'selected_total': selected_total})

    return records, (grand_total if has_totals else None)


def get_field_level(field):
    level = 0
    current = field.parent
    while current is not None:
        level += 1
        current = current.parent
    return level


def generate_code():
    return f'{secrets.randbelow(1000000):06d}'


def normalize_email(email):
    return email.strip().lower()
