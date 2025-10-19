from django.contrib import admin
from django.urls import path, include
from blog_main import views
from blogs.views import blog_detail, search, home, posts_by_category, legal_page_detail, contact_us, write_for_us
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from .sitemaps import BlogSitemap, CategorySitemap, StaticSitemap, LegalSitemap

# Sitemap configuration
sitemaps = {
    'blogs': BlogSitemap,
    'categories': CategorySitemap,
    'static': StaticSitemap,
    'legal': LegalSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),

    # ✅ Include all blog-related URLs here
    path('blogs/', include('blogs.urls')),
    path('category/', include('blogs.urls')),



    # Individual blog detail (keep separate)
    path('blogs/<slug:slug>/', blog_detail, name='blog_detail'),

    path('category/<int:category_id>/',
         posts_by_category, name='posts_by_category'),
    # Add this new line for the category list page

    path('search/', search, name='search'),

    # ✅ Add Legal Pages URLs here
    path('privacy/', legal_page_detail,
         {'page_type': 'PRIVACY'}, name='privacy'),
    path('terms/', legal_page_detail, {'page_type': 'TERMS'}, name='terms'),
    path('cookie-policy/', legal_page_detail,
         {'page_type': 'COOKIE'}, name='cookie_policy'),
    path('disclaimer/', legal_page_detail,
         {'page_type': 'DISCLAIMER'}, name='disclaimer'),
    path('about/', legal_page_detail, {'page_type': 'ABOUT'}, name='about'),

    # ✅ Contact Pages (moved from blogs/urls.py to avoid conflicts)
    path('contact/', contact_us, name='contact_us'),
    path('write-for-us/', write_for_us, name='write_for_us'),

    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', include('dashboards.urls')),

    # SEO enhancements
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', include('robots.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# For serving static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
