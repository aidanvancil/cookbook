import base64
from django import template

register = template.Library()

@register.filter
def base64_encode(value):
    return base64.b64encode(value.encode()).decode('utf-8')

@register.filter
def base64_decode(value):
    return base64.b64decode(value.encode()).decode('utf-8')
