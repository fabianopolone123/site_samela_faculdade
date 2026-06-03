from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_dynamic_topics_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='costtopic',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='descrição'),
        ),
    ]
