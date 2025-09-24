from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blogs.models import Blogs, Category

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'http'  # ← Add this line

    def items(self):
        return Blogs.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = 'http'  # ← Add this line

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('posts_by_category', kwargs={'category_id': obj.id})

class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'
    protocol = 'http'  # ← Add this line

    def items(self):
        return ['home', 'search']

    def location(self, item):
        return reverse(item)