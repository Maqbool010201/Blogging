# blogs/mixins.py
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.core.exceptions import ImproperlyConfigured

class SmartCanonicalMixin:
    """
    Mixin for generating canonical URLs with smart parameter handling
    """
    canonical_view_name = None
    canonical_ignore_params = ['utm_source', 'utm_medium', 'utm_campaign', 'fbclid']
    canonical_include_params = []  # Specific params to keep
    
    def get_canonical_url(self):
        """
        Generate canonical URL with smart parameter handling
        """
        try:
            # Check if we have an object with get_absolute_url method
            if hasattr(self, 'object') and self.object is not None:
                if hasattr(self.object, 'get_absolute_url'):
                    absolute_url = self.object.get_absolute_url()
                    if absolute_url:
                        return self.request.build_absolute_uri(absolute_url)
            
            # Use canonical_view_name or fall back to current path
            if self.canonical_view_name:
                url = reverse(self.canonical_view_name)
            else:
                url = self.request.path_info
            
            # Handle query parameters
            params = {}
            if self.canonical_include_params:
                for param in self.canonical_include_params:
                    if param in self.request.GET:
                        params[param] = self.request.GET[param]
            
            if params:
                url = f"{url}?{urlencode(params)}"
                
            return self.request.build_absolute_uri(url)
            
        except Exception as e:
            # Fallback to current URL if anything goes wrong
            return self.request.build_absolute_uri(self.request.path)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['canonical_url'] = self.get_canonical_url()
        return context


class BreadcrumbMixin:
    """
    Mixin to automatically generate breadcrumbs for views
    """
    breadcrumbs = []
    
    def get_breadcrumbs(self):
        """
        Generate breadcrumb trail. Override this in specific views if needed.
        Format: [('Title', 'url_name_or_url'), ...]
        """
        return self.breadcrumbs
    
    def resolve_breadcrumb_url(self, url_item):
        """
        Resolve URL whether it's a named URL pattern or direct URL
        """
        if url_item is None or url_item == '':
            return None  # No URL for current page
        
        try:
            if isinstance(url_item, str) and ':' in url_item:
                # It's a named URL pattern like 'blog_list'
                return reverse(url_item)
            elif isinstance(url_item, str):
                # It's a direct URL
                return url_item
            elif callable(url_item):
                # It's a callable that returns a URL
                return url_item()
            return url_item
        except Exception:
            # If URL resolution fails, return None
            return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Build breadcrumbs
        breadcrumb_data = []
        breadcrumbs = self.get_breadcrumbs()
        
        for title, url in breadcrumbs:
            resolved_url = self.resolve_breadcrumb_url(url)
            breadcrumb_data.append({
                'title': title,
                'url': resolved_url
            })
        
        context['breadcrumbs'] = breadcrumb_data
        return context