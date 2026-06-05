from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def _to_decimal(value):
    if value is None or value == '':
        return Decimal('0')
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal('0')


@register.filter
def currency_br(value):
    decimal_value = _to_decimal(value)
    rendered = f'{decimal_value:,.2f}'
    return rendered.replace(',', 'X').replace('.', ',').replace('X', '.')
