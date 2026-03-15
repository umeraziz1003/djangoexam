from django import template

from accounts.permissions import can as can_check

register = template.Library()


@register.simple_tag
def can(user, module, action):
    return can_check(user, module, action)
