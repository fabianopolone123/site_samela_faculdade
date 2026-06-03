from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_quote_quantity_freight'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='CostRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('topic', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='records', to='accounts.costtopic')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='CostField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('field_type', models.CharField(choices=[('texto', 'Texto'), ('numero', 'Número'), ('link', 'Link'), ('valor', 'Valor')], max_length=20, verbose_name='tipo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='children', to='accounts.costfield')),
                ('topic', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='fields', to='accounts.costtopic')),
            ],
            options={'ordering': ['created_at']},
        ),
        migrations.CreateModel(
            name='CostRecordValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, verbose_name='valor')),
                ('field', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='record_values', to='accounts.costfield')),
                ('record', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='values', to='accounts.costrecord')),
            ],
            options={'unique_together': {('record', 'field')}},
        ),
    ]
