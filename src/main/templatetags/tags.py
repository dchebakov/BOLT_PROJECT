from django import template

register = template.Library()


@register.filter('typename')
def typename(object):
    return object.__class__.__name__


@register.filter('shortern')
def shorten(str):
    if len(str) < 20:
        return str
    return str[:20] + '...'
