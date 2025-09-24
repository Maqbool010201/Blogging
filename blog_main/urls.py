from django.contrib import admin
from django.urls import path, include
from blog_main import views
from blogs.views import blog_detail, search, home, posts_by_category
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from . import sitemaps
from .sitemaps import BlogSitemap, CategorySitemap, StaticViewSitemap

# Sitemap configuration
sitemaps = {
    'blogs': BlogSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('category/<int:category_id>/', posts_by_category, name='posts_by_category'),
    path('search/', search, name='search'),
    path('blogs/<slug:slug>/', blog_detail, name='blog_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', include('dashboards.urls')),
    
    # SEO enhancements
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', include('robots.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# For serving static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)