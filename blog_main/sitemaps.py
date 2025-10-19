# blogs/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blogs.models import Blogs, Category, LegalPage

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'  # Use 'http' for development

    def items(self):
        return Blogs.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = 'https'

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # Reverse to category posts page
        return reverse('posts_by_category', kwargs={'category_id': obj.id})

class StaticSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        # Add all static pages here
        return ['home', 'search', 'contact_us', 'write_for_us']

    def location(self, item):
        return reverse(item)

class LegalSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.3
    protocol = 'https'

    def items(self):
        # Only published legal pages
        return LegalPage.objects.filter(is_published=True)

    def location(self, obj):
        # Map page_type to correct URL name in urls.py
        page_map = {
            'PRIVACY': 'privacy',
            'TERMS': 'terms',
            'COOKIE': 'cookie_policy',
            'DISCLAIMER': 'disclaimer',
            'ABOUT': 'about',
        }
        url_name = page_map.get(obj.page_type)
        if url_name:
            return reverse(url_name)
        # Fallback to home if page_type is not mapped
        return reverse('home')
