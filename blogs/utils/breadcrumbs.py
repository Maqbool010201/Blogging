# blogs/utils/breadcrumbs.py
from django.urls import resolve, Resolver404
from django.utils.text import slugify

class Breadcrumb:
    def __init__(self, title, url=None, is_active=False):
        self.title = title
        self.url = url
        self.is_active = is_active

class BreadcrumbBuilder:
    def __init__(self, request):
        self.request = request
        self.breadcrumbs = []
    
    def add(self, title, url=None, is_active=False):
        breadcrumb = Breadcrumb(title, url, is_active)
        self.breadcrumbs.append(breadcrumb)
        return self
    
    def auto_detect_from_url(self):
        """Automatically generate breadcrumbs from URL pattern"""
        path_components = self.request.path_info.strip('/').split('/')
        accumulated_path = ''
        
        for i, component in enumerate(path_components):
            accumulated_path += f'/{component}'
            
            try:
                match = resolve(accumulated_path)
                view_name = match.url_name
                
                # Skip numeric components (like category IDs)
                if component.isdigit():
                    # Try to get the object name from context or skip
                    continue
                
                # Map view names to breadcrumb titles
                title_map = {
                    'home': 'Home',
                    'blog_list': 'Blogs',
                    'post_list': 'Blog',
                    'post_detail': 'Article',
                    'category_list': 'Categories',
                    'category_posts': 'Category',  # Updated to handle category pages
                    'tag_list': 'Tags',
                    'search': 'Search Results',
                }
                
                title = title_map.get(view_name, component.replace('-', ' ').title())
                
                # For detail views, try to get object title
                if view_name == 'post_detail' and hasattr(match.func, 'view_class'):
                    try:
                        obj = match.func.view_class.model.objects.get(slug=component)
                        title = obj.title
                    except:
                        pass
                elif view_name == 'category_posts' and 'category' in self.request.resolver_match.kwargs:
                    # Get category name from URL parameter
                    from blogs.models import Category  # Import your Category model
                    try:
                        category_id = self.request.resolver_match.kwargs['category_id']
                        category = Category.objects.get(id=category_id)
                        title = category.category_name
                    except:
                        pass
                
                is_active = (i == len(path_components) - 1)
                url = accumulated_path if not is_active else None
                
                self.add(title, url, is_active)
                
            except Resolver404:
                # Skip numeric components and unknown paths that are likely IDs
                if not component.isdigit():
                    title = component.replace('-', ' ').title()
                    is_active = (i == len(path_components) - 1)
                    url = accumulated_path if not is_active else None
                    self.add(title, url, is_active)
        
        return self
    
    def build(self):
        return self.breadcrumbs