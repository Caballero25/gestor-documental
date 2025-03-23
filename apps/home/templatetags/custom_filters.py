from django import template

register = template.Library()

@register.filter
def filter_visible(submodules):
    return submodules.filter(is_visible=True)
