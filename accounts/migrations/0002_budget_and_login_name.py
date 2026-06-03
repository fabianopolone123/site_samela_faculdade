from django.contrib.auth.hashers import make_password
from django.db import migrations, models


def seed_initial_data(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    BudgetSection = apps.get_model('accounts', 'BudgetSection')

    BudgetSection.objects.update_or_create(
        code='5.1',
        defaults={
            'title': 'Custeio do projeto de pesquisa',
            'description': 'Cadastro inicial do topico 5.1 com produtos e tres orcamentos.',
        },
    )

    admin_user, _ = User.objects.get_or_create(
        email='adm@neevy.local',
        defaults={
            'login_name': 'adm',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'full_name': 'Administrador do sistema',
        },
    )
    admin_user.login_name = 'adm'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.full_name = 'Administrador do sistema'
    admin_user.password = make_password('123')
    admin_user.save()

    test_user, _ = User.objects.get_or_create(
        email='fabiano@neevy.local',
        defaults={
            'login_name': 'fabiano',
            'is_staff': False,
            'is_superuser': False,
            'is_active': True,
            'full_name': 'Fabiano teste',
        },
    )
    test_user.login_name = 'fabiano'
    test_user.is_staff = False
    test_user.is_superuser = False
    test_user.is_active = True
    test_user.full_name = 'Fabiano teste'
    test_user.password = make_password('123')
    test_user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='login_name',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True, verbose_name='login'),
        ),
        migrations.CreateModel(
            name='BudgetSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='codigo')),
                ('title', models.CharField(max_length=255, verbose_name='titulo')),
                ('description', models.TextField(blank=True, verbose_name='descricao')),
            ],
            options={'ordering': ['code']},
        ),
        migrations.CreateModel(
            name='BudgetProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome do produto')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('section', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='products', to='accounts.budgetsection')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='BudgetQuote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote_number', models.PositiveSmallIntegerField(verbose_name='orcamento')),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='preco')),
                ('quantity', models.PositiveIntegerField(verbose_name='quantidade')),
                ('link', models.URLField(verbose_name='link')),
                ('is_selected', models.BooleanField(default=False, verbose_name='selecionado')),
                ('product', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='quotes', to='accounts.budgetproduct')),
            ],
            options={
                'ordering': ['quote_number'],
                'unique_together': {('product', 'quote_number')},
            },
        ),
        migrations.RunPython(seed_initial_data, migrations.RunPython.noop),
    ]
