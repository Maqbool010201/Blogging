# blogs/context_processors.py
from .models import Category, SocialMedia
from django.conf import settings
from urllib.parse import urlencode
from .utils.breadcrumbs import BreadcrumbBuilder

def get_categories(request):
    """Provides all categories to templates"""
    categories = Category.objects.all()
    return {'categories': categories}


def advanced_canonical_url(request):
    """
    Generates SEO-friendly canonical URL:
    - Removes unwanted params
    - Removes all numeric query params (page numbers, tracking IDs)
    - Handles multi-language slugs
    - Handles AMP canonical links
    """
    path = request.path
    query_params = request.GET.copy()

    # Remove unwanted query parameters
    unwanted_params = ['utm_source', 'utm_medium', 'fbclid', 'gclid', 'sessionid']
    for param in unwanted_params:
        query_params.pop(param, None)

    # Remove all numeric query parameters dynamically
    numeric_keys = [key for key, value in query_params.items() if value.isdigit()]
    for key in numeric_keys:
        query_params.pop(key, None)

    # Remove page=1 specifically
    if query_params.get('page') == '1':
        query_params.pop('page', None)

    # Handle multi-language slugs (assume default language in settings.LANGUAGE_CODE)
    # Example: /ar/blog-title/ -> /blog-title/ for canonical
    path_parts = path.strip('/').split('/')
    if len(path_parts) > 0 and path_parts[0] in [lang[0] for lang in settings.LANGUAGES]:
        default_lang = settings.LANGUAGE_CODE
        if path_parts[0] != default_lang:
            path_parts = path_parts[1:]  # remove language code for canonical
    canonical_path = '/' + '/'.join(path_parts) + '/'

    # Build canonical URL
    canonical_url = request.build_absolute_uri(canonical_path)
    if query_params:
        canonical_url = f"{canonical_url}?{urlencode(query_params)}"

    # AMP canonical handling
    amp_canonical = None
    if path.startswith('/amp/'):
        standard_path = path.replace('/amp/', '/')
        amp_canonical = request.build_absolute_uri(standard_path)

    return {
        'canonical_url': canonical_url,
        'amp_canonical': amp_canonical,
        'query_params': query_params,
    }

def breadcrumbs(request):
    builder = BreadcrumbBuilder(request)
    breadcrumbs_list = builder.auto_detect_from_url().build()
    return {'breadcrumbs': breadcrumbs_list}

def seo_context(request):
    default_meta_title = "WiseMixMedia - Professional Blogging Platform"
    default_meta_description = "Your default blog description"
    return {
        'meta_title': default_meta_title,
        'meta_description': default_meta_description,
    }   

def social_media_links(request):
    """Add social media links to all templates"""
    return {
        'social_media_links': SocialMedia.objects.filter(is_active=True)
    }