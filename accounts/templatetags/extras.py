from django import template

register = template.Library()


@register.filter
def get_item(obj, key):
    if obj is None:
        return ""
    try:
        return obj.get(key, "")
    except AttributeError:
        return ""
