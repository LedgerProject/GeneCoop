from django import template
register = template.Library()

@register.filter
def org(value):
    """Replaces org token with html representation"""
    start_token = '<org>'
    end_token = '</org>'
    return value.replace(start_token,'<i class="organisation">').replace(end_token,'</i>&nbsp;<sup><i class="fa fa-briefcase"></i></sup>')

@register.filter
def tech(value):
    """Replaces tech token with html representation"""
    start_token = '<tech>'
    end_token = '</tech>'
    return value.replace(start_token,'<i class="technology">').replace(end_token,'</i>&nbsp;<sup><i class="fa fa-file-screen"></i></sup>')

@register.filter
def pd(value):
    """Replaces personal data token with html representation"""
    start_token = '<pd>'
    end_token = '</pd>'
    return value.replace(start_token,'<i class="personal_data">').replace(end_token,'</i>&nbsp;<sup><i class="fa fa-file-archive-o"></i></sup>')

register.filter('org', org)
register.filter('pd', pd)
register.filter('tech', tech)

