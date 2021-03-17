from django import template
register = template.Library()

@register.filter
def org(value):
    """Replaces org token with html representation"""
    start_token = '<org>'
    end_token = '</org>'
    return value.replace(start_token,'<b>').replace(end_token,'</b>')

@register.filter
def tech(value):
    """Replaces tech token with html representation"""
    start_token = '<tech>'
    end_token = '</tech>'
    return value.replace(start_token,'<b>').replace(end_token,'</b>')

@register.filter
def pd(value):
    """Replaces personal data token with html representation"""
    start_token = '<pd>'
    end_token = '</pd>'
    return value.replace(start_token,'<i>').replace(end_token,'</i>')

register.filter('org', org)
register.filter('pd', pd)
register.filter('tech', tech)

