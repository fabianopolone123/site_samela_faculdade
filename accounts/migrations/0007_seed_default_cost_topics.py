from django.db import migrations


DEFAULT_TOPICS = [
    {
        'name': 'Material permanente adquirido no país e importado',
        'aliases': ['Material permanente adquirido no país e importado;'],
        'description': (
            'Cadastro de produto com três orçamentos comparativos, contendo preço, '
            'link, quantidade, frete e seleção do orçamento considerado.'
        ),
        'fields': [
            {'name': 'Nome do produto', 'field_type': 'texto'},
            {
                'name': 'Orçamento 1',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                    {'name': 'Quantidade', 'field_type': 'numero'},
                    {'name': 'Frete', 'field_type': 'valor'},
                ],
            },
            {
                'name': 'Orçamento 2',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                    {'name': 'Quantidade', 'field_type': 'numero'},
                    {'name': 'Frete', 'field_type': 'valor'},
                ],
            },
            {
                'name': 'Orçamento 3',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                    {'name': 'Quantidade', 'field_type': 'numero'},
                    {'name': 'Frete', 'field_type': 'valor'},
                ],
            },
            {'name': 'Selecionar para orçar', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Material de consumo adquirido no país e importado',
        'description': (
            'Cadastro de material de consumo com três orçamentos, incluindo preço, '
            'link, quantidade, frete e seleção do orçamento utilizado.'
        ),
        'fields': [
            {'name': 'Nome do produto', 'field_type': 'texto'},
            {
                'name': 'Orçamento 1',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                    {'name': 'Quantidade', 'field_type': 'numero'},
                    {'name': 'Frete', 'field_type': 'valor'},
                ],
            },
            {
                'name': 'Orçamento 2',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                    {'name': 'Quantidade', 'field_type': 'numero'},
                    {'name': 'Frete', 'field_type': 'valor'},
                ],
            },
            {
                'name': 'Orçamento 3',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                    {'name': 'Quantidade', 'field_type': 'numero'},
                    {'name': 'Frete', 'field_type': 'valor'},
                ],
            },
            {'name': 'Selecionar para orçar', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Serviços de Terceiros contratados no país e no exterior',
        'description': (
            'Cadastro de serviços com três orçamentos comparativos, cada um com preço, '
            'link, frete e seleção do orçamento considerado.'
        ),
        'fields': [
            {'name': 'Nome do serviço', 'field_type': 'texto'},
            {
                'name': 'Orçamento 1',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                    {'name': 'Frete', 'field_type': 'valor'},
                ],
            },
            {
                'name': 'Orçamento 2',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                    {'name': 'Frete', 'field_type': 'valor'},
                ],
            },
            {
                'name': 'Orçamento 3',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                    {'name': 'Frete', 'field_type': 'valor'},
                ],
            },
            {'name': 'Selecionar para orçar', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Despesas de Transporte e Diárias',
        'description': (
            'Cadastro de despesas de deslocamento com origem, destino e três '
            'orçamentos comparativos para selecionar o valor considerado.'
        ),
        'fields': [
            {'name': 'Nome do meio de transporte', 'field_type': 'texto'},
            {'name': 'Origem', 'field_type': 'texto'},
            {'name': 'Destino', 'field_type': 'texto'},
            {
                'name': 'Orçamento 1',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                ],
            },
            {
                'name': 'Orçamento 2',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                ],
            },
            {
                'name': 'Orçamento 3',
                'field_type': 'texto',
                'children': [
                    {'name': 'Preço', 'field_type': 'valor'},
                    {'name': 'Link', 'field_type': 'link'},
                ],
            },
            {'name': 'Selecionar para orçar', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas como Item Orçamentário',
        'description': 'Estrutura geral para bolsas com modalidade, valor, quantidade e duração.',
        'fields': [
            {'name': 'Modalidade da bolsa', 'field_type': 'texto'},
            {'name': 'Valor orçamentário (por estudante)', 'field_type': 'valor'},
            {'name': 'Quantidade de estudantes', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — Iniciação Científica',
        'description': 'Bolsa com valor por estudante, quantidade e duração em meses.',
        'fields': [
            {'name': 'Valor orçamentário (por estudante)', 'field_type': 'valor'},
            {'name': 'Quantidade de estudantes', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — Mestrado',
        'description': 'Bolsa com valor por estudante, quantidade e duração em meses.',
        'fields': [
            {'name': 'Valor orçamentário (por estudante)', 'field_type': 'valor'},
            {'name': 'Quantidade de estudantes', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — Doutorado Direto',
        'description': 'Bolsa com valor por estudante, quantidade e duração em meses.',
        'fields': [
            {'name': 'Valor orçamentário (por estudante)', 'field_type': 'valor'},
            {'name': 'Quantidade de estudantes', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — Doutorado',
        'description': 'Bolsa com valor por estudante, quantidade e duração em meses.',
        'fields': [
            {'name': 'Valor orçamentário (por estudante)', 'field_type': 'valor'},
            {'name': 'Quantidade de estudantes', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — Pós-Doutorado',
        'description': (
            'Bolsa com valor por estudante, quantidade e duração em meses, com foco '
            'em seleção internacional quando aplicável.'
        ),
        'fields': [
            {'name': 'Valor orçamentário (por estudante)', 'field_type': 'valor'},
            {'name': 'Quantidade de estudantes', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — Jornalismo Científico (JC)',
        'description': 'Bolsa com valor por estudante, quantidade e duração em meses.',
        'fields': [
            {'name': 'Valor orçamentário (por estudante)', 'field_type': 'valor'},
            {'name': 'Quantidade de estudantes', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — Treinamento Técnico e Participação em Curso',
        'description': 'Bolsa com valor por estudante, quantidade e duração em meses.',
        'fields': [
            {'name': 'Valor orçamentário (por estudante)', 'field_type': 'valor'},
            {'name': 'Quantidade de estudantes', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — Ensino Público - Aperfeiçoamento Pedagógico (EP)',
        'description': 'Bolsa com valor por candidato, quantidade e duração em meses.',
        'fields': [
            {'name': 'Valor orçamentário (por candidato)', 'field_type': 'valor'},
            {'name': 'Quantidade de candidatos', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — EP-1 Aperfeiçoamento Pedagógico',
        'description': 'Para candidatos com nível superior, dedicação de 4 horas semanais.',
        'fields': [
            {'name': 'Valor orçamentário (por candidato)', 'field_type': 'valor'},
            {'name': 'Quantidade de candidatos', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — EP-2 Aperfeiçoamento Pedagógico',
        'description': 'Para candidatos com nível superior, dedicação de 8 horas semanais.',
        'fields': [
            {'name': 'Valor orçamentário (por candidato)', 'field_type': 'valor'},
            {'name': 'Quantidade de candidatos', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — EP-3 Aperfeiçoamento Pedagógico',
        'description': 'Para candidatos com mestrado concluído, dedicação de 4 horas semanais.',
        'fields': [
            {'name': 'Valor orçamentário (por candidato)', 'field_type': 'valor'},
            {'name': 'Quantidade de candidatos', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — EP-4 Aperfeiçoamento Pedagógico',
        'description': 'Para candidatos com mestrado concluído, dedicação de 8 horas semanais.',
        'fields': [
            {'name': 'Valor orçamentário (por candidato)', 'field_type': 'valor'},
            {'name': 'Quantidade de candidatos', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — EP-5 Aperfeiçoamento Pedagógico',
        'description': 'Para candidatos com doutorado concluído, dedicação de 4 horas semanais.',
        'fields': [
            {'name': 'Valor orçamentário (por candidato)', 'field_type': 'valor'},
            {'name': 'Quantidade de candidatos', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
    {
        'name': 'Bolsas — EP-6 Aperfeiçoamento Pedagógico',
        'description': 'Para candidatos com doutorado concluído, dedicação de 8 horas semanais.',
        'fields': [
            {'name': 'Valor orçamentário (por candidato)', 'field_type': 'valor'},
            {'name': 'Quantidade de candidatos', 'field_type': 'numero'},
            {'name': 'Duração em meses', 'field_type': 'numero'},
        ],
    },
]


def ensure_field(cost_field_model, topic, field_data, parent=None):
    field, created = cost_field_model.objects.get_or_create(
        topic=topic,
        parent=parent,
        name=field_data['name'],
        defaults={'field_type': field_data['field_type']},
    )
    if not created and field.field_type != field_data['field_type']:
        field.field_type = field_data['field_type']
        field.save(update_fields=['field_type'])

    for child_data in field_data.get('children', []):
        ensure_field(cost_field_model, topic, child_data, parent=field)


def seed_default_topics(apps, schema_editor):
    cost_topic_model = apps.get_model('accounts', 'CostTopic')
    cost_field_model = apps.get_model('accounts', 'CostField')

    for topic_data in DEFAULT_TOPICS:
        aliases = topic_data.get('aliases', [])
        topic = cost_topic_model.objects.filter(name=topic_data['name']).first()
        if topic is None:
            for alias in aliases:
                topic = cost_topic_model.objects.filter(name=alias).first()
                if topic is not None:
                    break

        if topic is None:
            topic = cost_topic_model.objects.create(
                name=topic_data['name'],
                description=topic_data.get('description', ''),
            )
        else:
            changed = False
            if topic.name != topic_data['name']:
                topic.name = topic_data['name']
                changed = True
            if topic.description != topic_data.get('description', ''):
                topic.description = topic_data.get('description', '')
                changed = True
            if changed:
                topic.save(update_fields=['name', 'description'])

        for field_data in topic_data['fields']:
            ensure_field(cost_field_model, topic, field_data)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_costtopic_description'),
    ]

    operations = [
        migrations.RunPython(seed_default_topics, migrations.RunPython.noop),
    ]
