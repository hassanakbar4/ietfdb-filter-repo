from django import template

register = template.Library()

@register.simple_tag
def get_field_value(obj, name):
    if name=="resources":
        m2m = getattr(obj, name)
        return ', '.join([x.desc for x in m2m.all()])
    return getattr(obj, name)
