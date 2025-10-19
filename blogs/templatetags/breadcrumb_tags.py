# blogs/templatetags/breadcrumb_tags.py
from django import template
from blogs.utils.breadcrumbs import BreadcrumbBuilder

register = template.Library()

@register.simple_tag(takes_context=True)
def get_breadcrumbs(context):
    """
    Returns breadcrumbs for the current request.
    Usage: {% get_breadcrumbs as breadcrumbs %}
    """
    request = context['request']
    builder = BreadcrumbBuilder(request)
    return builder.auto_detect_from_url().build()
