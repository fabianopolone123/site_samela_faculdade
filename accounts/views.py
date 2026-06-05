import secrets
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    AllowedSignupEmailForm,
    LoginForm,
    SignupCodeForm,
    SignupEmailForm,
    SignupPasswordForm,
    TopicDescriptionForm,
    TopicFieldForm,
    TopicForm,
)
from .models import (
    AuditLog,
    AllowedSignupEmail,
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


def _send_utf8_mail(subject, body, to):
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
    )
    msg.encoding = 'utf-8'
    msg.send(fail_silently=False)


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
def allowed_signup_emails_view(request):
    if not request.user.is_staff:
        messages.error(request, 'A gestão de e-mails está disponível apenas para o login de administração.')
        return redirect('dashboard')

    dynamic_emails = list(AllowedSignupEmail.objects.all())
    dynamic_values = {item.email for item in dynamic_emails}
    fixed_emails = sorted(settings.ALLOWED_SIGNUP_EMAILS - dynamic_values)
    context = {
        'email_form': AllowedSignupEmailForm(),
        'fixed_emails': fixed_emails,
        'dynamic_emails': dynamic_emails,
    }
    return render(request, 'accounts/allowed_signup_emails.html', context)


@login_required
def create_allowed_signup_email_view(request):
    if request.method != 'POST':
        return redirect('allowed_signup_emails')
    if not request.user.is_staff:
        messages.error(request, 'A gestão de e-mails está disponível apenas para o login de administração.')
        return redirect('dashboard')

    form = AllowedSignupEmailForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Informe um e-mail válido para liberar o cadastro.')
        return redirect('allowed_signup_emails')

    email = normalize_email(form.cleaned_data['email'])
    if email in settings.ALLOWED_SIGNUP_EMAILS or AllowedSignupEmail.objects.filter(email=email).exists():
        messages.info(request, 'Este e-mail já está autorizado para cadastro.')
        return redirect('allowed_signup_emails')

    AllowedSignupEmail.objects.create(email=email)
    register_audit_log(
        request.user,
        AuditLog.ACTION_CREATE,
        'E-mail autorizado',
        email,
        'Liberação de novo e-mail para o fluxo de cadastro.',
    )
    messages.success(request, 'E-mail autorizado cadastrado com sucesso.')
    return redirect('allowed_signup_emails')


@login_required
def delete_allowed_signup_email_view(request, email_id):
    if request.method != 'POST':
        return redirect('allowed_signup_emails')
    if not request.user.is_staff:
        messages.error(request, 'A gestão de e-mails está disponível apenas para o login de administração.')
        return redirect('dashboard')

    allowed_email = get_object_or_404(AllowedSignupEmail, id=email_id)
    email = allowed_email.email
    allowed_email.delete()
    register_audit_log(
        request.user,
        AuditLog.ACTION_DELETE,
        'E-mail autorizado',
        email,
        'Remoção de e-mail da lista dinâmica de cadastro.',
    )
    messages.success(request, 'E-mail autorizado removido com sucesso.')
    return redirect('allowed_signup_emails')


@login_required
def audit_log_view(request):
    if not request.user.is_staff:
        messages.error(request, 'A auditoria está disponível apenas para o login de administração.')
        return redirect('dashboard')

    audit_logs = AuditLog.objects.select_related('user').all()[:300]
    return render(request, 'accounts/audit_log.html', {'audit_logs': audit_logs})


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
        build_record_cards(selected_topic, selected_rows) if selected_topic else ([], Decimal('0'))
    )

    all_topics_total = sum(calculate_topic_total(topic) for topic in topics)

    context = {
        'topics': topics,
        'selected_topic': selected_topic,
        'topic_form': TopicForm(),
        'field_form': TopicFieldForm(topic=selected_topic),
        'description_form': TopicDescriptionForm(
            initial={'description': selected_topic.description} if selected_topic else {}
        ),
        'selected_rows': selected_rows,
        'selected_groups': selected_groups,
        'selected_records': selected_records,
        'topic_grand_total': topic_grand_total,
        'all_topics_total': all_topics_total,
    }
    return render(request, 'accounts/budget_product_form.html', context)


@login_required
def create_topic_view(request):
    if request.method != 'POST':
        return redirect('budget_product_create')

    form = TopicForm(request.POST)
    if form.is_valid():
        topic = CostTopic.objects.create(name=form.cleaned_data['name'])
        register_audit_log(
            request.user,
            AuditLog.ACTION_CREATE,
            'Tópico',
            topic.name,
            'Cadastro de novo tópico na área de custos.',
        )
        messages.success(request, 'Tópico cadastrado com sucesso.')
        return redirect(f"{reverse('budget_product_create')}?topic={topic.id}")

    messages.error(request, 'Não foi possível cadastrar o tópico.')
    return redirect('budget_product_create')


@login_required
def delete_topic_view(request, topic_id):
    if request.method != 'POST':
        return redirect('budget_product_create')

    topic = get_object_or_404(CostTopic, id=topic_id)
    topic_name = topic.name
    topic.delete()
    register_audit_log(
        request.user,
        AuditLog.ACTION_DELETE,
        'Tópico',
        topic_name,
        'Exclusão do tópico e dos registros vinculados.',
    )
    messages.success(request, 'Tópico excluído com sucesso.')
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
        register_audit_log(
            request.user,
            AuditLog.ACTION_CREATE,
            'Campo',
            form.cleaned_data['name'],
            f'Cadastro de campo no tópico {topic.name}.',
        )
        messages.success(request, 'Campo cadastrado com sucesso.')
    else:
        messages.error(request, 'Não foi possível cadastrar o campo.')

    return redirect(f"{reverse('budget_product_create')}?topic={topic.id}&open=campos")


@login_required
def update_topic_description_view(request, topic_id):
    if request.method != 'POST':
        return redirect('budget_product_create')
    topic = get_object_or_404(CostTopic, id=topic_id)
    form = TopicDescriptionForm(request.POST)
    if form.is_valid():
        topic.description = form.cleaned_data['description']
        topic.save()
        register_audit_log(
            request.user,
            AuditLog.ACTION_UPDATE,
            'Tópico',
            topic.name,
            'Atualização da observação do tópico.',
        )
        messages.success(request, 'Observação salva com sucesso.')
    else:
        messages.error(request, 'Não foi possível salvar a observação.')
    return redirect(f"{reverse('budget_product_create')}?topic={topic_id}")


@login_required
def delete_topic_field_view(request, field_id):
    if request.method != 'POST':
        return redirect('budget_product_create')

    field = get_object_or_404(CostField, id=field_id)
    topic_id = field.topic_id
    field_name = field.name
    topic_name = field.topic.name
    field.delete()
    register_audit_log(
        request.user,
        AuditLog.ACTION_DELETE,
        'Campo',
        field_name,
        f'Exclusão de campo do tópico {topic_name}.',
    )
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
        if field.field_type == 'valor' and value:
            parsed_value = parse_decimal_input(value)
            if parsed_value is not None:
                value = format_decimal_br(parsed_value)
        if value:
            CostRecordValue.objects.create(record=record, field=field, value=value)
            saved_values += 1

    if saved_values == 0:
        record.delete()
        messages.error(request, 'Preencha ao menos um campo para salvar o novo custo.')
    else:
        register_audit_log(
            request.user,
            AuditLog.ACTION_CREATE,
            'Custo',
            get_record_title_from_record(record),
            f'Cadastro de novo custo no tópico {topic.name}.',
        )
        messages.success(request, 'Novo custo cadastrado com sucesso.')

    return redirect(f"{reverse('budget_product_create')}?topic={topic.id}")


@login_required
def delete_topic_record_view(request, record_id):
    if request.method != 'POST':
        return redirect('budget_product_create')

    record = get_object_or_404(CostRecord, id=record_id)
    topic_id = record.topic_id
    topic_name = record.topic.name
    record_title = get_record_title_from_record(record)
    next_url = request.POST.get('next', '').strip()
    record.delete()
    register_audit_log(
        request.user,
        AuditLog.ACTION_DELETE,
        'Custo',
        record_title,
        f'Exclusão de custo do tópico {topic_name}.',
    )
    messages.success(request, 'Custo excluído com sucesso.')

    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect(f"{reverse('budget_product_create')}?topic={topic_id}")


@login_required
def budget_ready_view(request):
    all_topics = list(
        CostTopic.objects.prefetch_related('fields', 'records__values__field').all()
    )
    topic_blocks = []
    all_topics_total = Decimal('0')

    for topic in all_topics:
        rows = build_topic_rows(topic)
        records, topic_total = build_record_cards(topic, rows)
        topic_blocks.append(
            {
                'topic': topic,
                'records': records,
                'topic_total': topic_total,
            }
        )
        all_topics_total += topic_total

    context = {
        'project_budget_title': PROJECT_BUDGET_TITLE,
        'project_budget_description': PROJECT_BUDGET_DESCRIPTION,
        'topic_blocks': topic_blocks,
        'all_topics_total': all_topics_total,
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

    if email not in get_allowed_signup_emails():
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

    _send_utf8_mail(
        subject='Seu código de acesso ao portal',
        body=(
            f'Seu código de verificação é: {signup_code.code}\n\n'
            f'Validade: {settings.SIGNUP_CODE_EXPIRATION_MINUTES} minutos.\n'
            'Se você não solicitou este cadastro, ignore esta mensagem.'
        ),
        to=[email],
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

    _send_utf8_mail(
        subject='Conta criada com sucesso no portal NEEVY - UFSCar',
        body=(
            'Seu cadastro foi concluído com sucesso.\n\n'
            f'E-mail de acesso: {user.email}\n'
            f'Data de criação: {timezone.localtime().strftime("%d/%m/%Y %H:%M")}\n'
            'A partir de agora você já pode fazer login no portal.'
        ),
        to=[user.email],
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
            elif name_lower == 'quantidade':
                field_role = 'quantidade'
                current_group['has_price_calc'] = True
            elif name_lower == 'frete':
                field_role = 'frete'
                current_group['has_price_calc'] = True
            else:
                field_role = None
            current_group['children'].append({**row, 'field_role': field_role})

    return groups


def calculate_topic_total(topic):
    all_fields = list(topic.fields.all())
    total = Decimal('0')
    for record in topic.records.prefetch_related('values__field').all():
        topic_total = get_selected_total_for_record(record, all_fields)
        if topic_total is not None:
            total += topic_total
    return total


def get_selected_total_for_record(record, topic_fields):
    values_map = {record_value.field_id: record_value.value for record_value in record.values.all()}

    selector = next(
        (field for field in topic_fields if field.parent_id is None and 'selecionar' in field.name.lower()),
        None,
    )
    if not selector:
        return None

    selected_str = values_map.get(selector.id, '').strip()
    if not selected_str:
        return None

    budget_parent = next(
        (
            field for field in topic_fields
            if field.parent_id is None and field.name.strip() == f'Orçamento {selected_str}'
        ),
        None,
    )
    if not budget_parent:
        return None

    price_value = Decimal('0')
    quantity_value = Decimal('1')
    freight_value = Decimal('0')

    for field in topic_fields:
        if field.parent_id != budget_parent.id:
            continue
        value_str = values_map.get(field.id, '').strip()
        if not value_str:
            continue
        amount = parse_decimal_input(value_str)
        if amount is None:
            continue
        name_lower = field.name.lower().strip()
        if name_lower in ('preço', 'preco'):
            price_value = amount
        elif name_lower == 'quantidade':
            quantity_value = amount
        elif name_lower == 'frete':
            freight_value = amount

    return (price_value * quantity_value) + freight_value


def build_record_cards(topic, selected_rows):
    field_order = {row['field'].id: index for index, row in enumerate(selected_rows)}
    all_fields = list(topic.fields.all())
    records = []
    grand_total = Decimal('0')

    for index, record in enumerate(topic.records.all(), start=1):
        values = sorted(
            [
                {
                    'field_name': value.field.name,
                    'field_type': value.field.get_field_type_display(),
                    'field_type_code': value.field.field_type,
                    'value': value.value,
                    'display_value': format_value_for_display(value.field.field_type, value.value),
                    'is_url_value': is_probably_url(value.value),
                    'level': get_field_level(value.field),
                    'order': field_order.get(value.field_id, 9999),
                }
                for value in record.values.all()
            ],
            key=lambda item: item['order'],
        )
        record_title = get_record_title(values, index)
        selected_total = get_selected_total_for_record(record, all_fields)
        if selected_total is not None:
            grand_total += selected_total
        records.append(
            {
                'record': record,
                'record_title': record_title,
                'values': values,
                'selected_total': selected_total,
            }
        )

    return records, grand_total


def get_record_title(values, index):
    preferred_keywords = (
        'nome do produto',
        'nome do serviço',
        'nome do meio de transporte',
        'modalidade da bolsa',
        'modalidade',
        'origem',
    )
    for item in values:
        field_name = item['field_name'].lower()
        if any(keyword in field_name for keyword in preferred_keywords) and item['value'].strip():
            return item['value']

    for item in values:
        if item['value'].strip():
            return item['value']

    return f'Cadastro {index}'


def get_record_title_from_record(record):
    values = [
        {
            'field_name': value.field.name,
            'value': value.value,
        }
        for value in record.values.select_related('field').all()
    ]
    return get_record_title(values, record.id or 0)


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


def get_allowed_signup_emails():
    dynamic_emails = set(AllowedSignupEmail.objects.values_list('email', flat=True))
    return set(settings.ALLOWED_SIGNUP_EMAILS) | dynamic_emails


def parse_decimal_input(value_str):
    cleaned = value_str.strip().replace('R$', '').replace(' ', '')
    if not cleaned:
        return None

    if ',' in cleaned:
        cleaned = cleaned.replace('.', '').replace(',', '.')

    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def format_decimal_br(value):
    rendered = f'{value:,.2f}'
    return rendered.replace(',', 'X').replace('.', ',').replace('X', '.')


def format_value_for_display(field_type_code, value):
    if field_type_code == 'valor':
        parsed = parse_decimal_input(value)
        if parsed is not None:
            return format_decimal_br(parsed)
    return value


def is_probably_url(value):
    normalized = value.strip().lower()
    return normalized.startswith('http://') or normalized.startswith('https://')


def register_audit_log(user, action, target_type, target_name, description=''):
    AuditLog.objects.create(
        user=user if getattr(user, 'is_authenticated', False) else None,
        action=action,
        target_type=target_type,
        target_name=target_name,
        description=description,
    )
