from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_budget_cost_entry'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetcostquote',
            name='freight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='frete'),
        ),
        migrations.AddField(
            model_name='budgetcostquote',
            name='quantity',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='quantidade'),
        ),
    ]
