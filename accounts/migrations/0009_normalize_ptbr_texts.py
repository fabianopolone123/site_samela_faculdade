from django.db import migrations


def repair_text(value):
    if not isinstance(value, str):
        return value
    if not any(token in value for token in ('Ã', 'Â', 'â')):
        return value
    try:
        return value.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def normalize_ptbr_texts(apps, schema_editor):
    model_fields = [
        ('accounts', 'BudgetSection', ['title', 'description']),
        ('accounts', 'CostTopic', ['name', 'description']),
        ('accounts', 'CostField', ['name']),
    ]

    for app_label, model_name, field_names in model_fields:
        model = apps.get_model(app_label, model_name)
        for obj in model.objects.all():
            changed_fields = []
            for field_name in field_names:
                original = getattr(obj, field_name)
                normalized = repair_text(original)
                if normalized != original:
                    setattr(obj, field_name, normalized)
                    changed_fields.append(field_name)
            if changed_fields:
                obj.save(update_fields=changed_fields)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_budgetcostentry_selected_quote_number_and_more'),
    ]

    operations = [
        migrations.RunPython(normalize_ptbr_texts, migrations.RunPython.noop),
    ]
