from django import template

register = template.Library()

@register.filter
def filter_visible(submodules):
    return submodules.filter(is_visible=True)

@register.filter
def filter_visible_by_perm(submodules, user):
    if not user:
        return []
    
    # Si es superusuario, ve todo lo que esté marcado como is_visible
    if user.is_superuser:
        return submodules.filter(is_visible=True)

    visible_submodules = submodules.filter(is_visible=True)
    allowed_submodules = []
    
    for submodule in visible_submodules:
        if not submodule.permission_required or user.has_perm(submodule.permission_required):
            allowed_submodules.append(submodule)
            
    return allowed_submodules
