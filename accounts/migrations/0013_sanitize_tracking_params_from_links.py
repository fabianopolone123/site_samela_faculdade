from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.db import migrations


def sanitize_external_url(url):
    raw_url = (url or '').strip()
    if not raw_url:
        return raw_url

    try:
        parts = urlsplit(raw_url)
    except ValueError:
        return raw_url

    cleaned_query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith('utm_')
    ]
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(cleaned_query, doseq=True),
            parts.fragment,
        )
    )


def sanitize_saved_links(apps, schema_editor):
    CostRecordValue = apps.get_model('accounts', 'CostRecordValue')
    BudgetQuote = apps.get_model('accounts', 'BudgetQuote')
    BudgetCostQuote = apps.get_model('accounts', 'BudgetCostQuote')

    for value in CostRecordValue.objects.select_related('field').filter(field__field_type='link'):
        cleaned = sanitize_external_url(value.value)
        if cleaned != value.value:
            value.value = cleaned
            value.save(update_fields=['value'])

    for quote in BudgetQuote.objects.all():
        cleaned = sanitize_external_url(quote.link)
        if cleaned != quote.link:
            quote.link = cleaned
            quote.save(update_fields=['link'])

    for quote in BudgetCostQuote.objects.all():
        cleaned = sanitize_external_url(quote.link)
        if cleaned != quote.link:
            quote.link = cleaned
            quote.save(update_fields=['link'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_costfield_calculation_role'),
    ]

    operations = [
        migrations.RunPython(sanitize_saved_links, migrations.RunPython.noop),
    ]
