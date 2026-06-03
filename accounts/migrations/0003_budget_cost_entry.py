from django.db import migrations, models


def seed_budget_sections(apps, schema_editor):
    BudgetSection = apps.get_model('accounts', 'BudgetSection')

    sections = [
        ('a', 'Material permanente adquirido no país ou importado', 'Equipamentos, aparelhos, mobiliários, instrumentos e demais bens duráveis necessários à execução da pesquisa.', None),
        ('b', 'Material de consumo adquirido no país ou importado', 'Materiais utilizados diretamente no desenvolvimento da pesquisa, como papelaria, materiais pedagógicos, insumos e itens consumíveis.', None),
        ('c', 'Serviços de terceiros contratados no país ou no exterior', 'Serviços técnicos, especializados ou operacionais diretamente vinculados aos objetivos do projeto.', None),
        ('d', 'Despesas de transporte e diárias', 'Despesas de deslocamento e permanência necessárias à realização de atividades diretamente ligadas à pesquisa.', None),
        ('d.1', 'Transporte', 'Passagem aérea, ônibus, táxi, aplicativo, combustível, pedágio e afins.', 'd'),
        ('d.2', 'Diárias', 'Diárias no país ou no exterior conforme normas vigentes da FAPESP.', 'd'),
        ('e', 'Bolsas como item orçamentário', 'Bolsas solicitadas como item orçamentário, de acordo com as normas específicas da FAPESP.', None),
    ]

    created = {}
    for code, title, description, parent_code in sections:
        parent = created.get(parent_code) if parent_code else None
        section, _ = BudgetSection.objects.update_or_create(
            code=code,
            defaults={'title': title, 'description': description, 'parent': parent},
        )
        created[code] = section


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_budget_and_login_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetsection',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='children', to='accounts.budgetsection'),
        ),
        migrations.CreateModel(
            name='BudgetCostEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='titulo')),
                ('details', models.TextField(blank=True, verbose_name='detalhes')),
                ('justification', models.TextField(blank=True, verbose_name='justificativa')),
                ('quantity', models.PositiveIntegerField(blank=True, null=True, verbose_name='quantidade')),
                ('unit', models.CharField(blank=True, max_length=100, verbose_name='unidade')),
                ('selected_quote_number', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='orcamento selecionado')),
                ('data', models.JSONField(blank=True, default=dict, verbose_name='dados extras')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('section', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='cost_entries', to='accounts.budgetsection')),
            ],
            options={'ordering': ['section__code', 'created_at']},
        ),
        migrations.CreateModel(
            name='BudgetCostQuote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote_number', models.PositiveSmallIntegerField(verbose_name='orcamento')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='valor')),
                ('link', models.URLField(verbose_name='link')),
                ('entry', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='quotes', to='accounts.budgetcostentry')),
            ],
            options={'ordering': ['quote_number'], 'unique_together': {('entry', 'quote_number')}},
        ),
        migrations.RunPython(seed_budget_sections, migrations.RunPython.noop),
    ]
