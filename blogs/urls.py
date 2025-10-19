# blogs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # All blog posts or category list
    path('', views.blog_list, name='blog_list'),
    path('category/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.posts_by_category, name='posts_by_category'),

    # Ad tracking routes
    path('ads/<int:ad_id>/impression/',
         views.record_ad_impression, name='record_impression'),
    path('ads/<int:ad_id>/click/', views.record_ad_click, name='record_click'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('send-newsletter/', views.send_custom_newsletter, name='send_custom_newsletter'),

    
]
