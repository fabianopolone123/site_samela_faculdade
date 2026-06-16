from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_costfield_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costfield',
            name='field_type',
            field=models.CharField(
                choices=[
                    ('texto', 'Texto'),
                    ('numero', 'Número'),
                    ('link', 'Link'),
                    ('valor', 'Valor'),
                    ('booleano', 'Sim/Não'),
                ],
                max_length=20,
                verbose_name='tipo',
            ),
        ),
    ]
