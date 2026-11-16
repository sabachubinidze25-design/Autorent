from django import template

from portal.services import money

register = template.Library()


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(key, "")
    except AttributeError:
        return ""


@register.filter(name="money")
def money_filter(value):
    return money(value) if value not in (None, "") else ""
