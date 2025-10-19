# middleware.py
from blogs.utils.breadcrumbs import BreadcrumbBuilder

class BreadcrumbMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only set auto breadcrumbs if not already set by view
        if not hasattr(request, 'breadcrumbs'):
            request.breadcrumbs = BreadcrumbBuilder(request).auto_detect_from_url().build()
        
        response = self.get_response(request)
        return response