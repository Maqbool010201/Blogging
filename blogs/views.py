from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.db.models import Q
from .models import Blogs, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def home(request):
    # Get featured posts that are published
    featured_post = Blogs.objects.filter(status='published', is_featured=True).select_related('category', 'author').order_by('-created_at')
    
    # Get regular posts that are published and not featured
    regular_posts = Blogs.objects.filter(status='published', is_featured=False).select_related('category', 'author').order_by('-created_at')
    
    # Pagination for regular posts
    paginator = Paginator(regular_posts, 10)  # Show 10 posts per page
    page = request.GET.get('page')
    
    try:
        regular_posts = paginator.page(page)
    except PageNotAnInteger:
        regular_posts = paginator.page(1)
    except EmptyPage:
        regular_posts = paginator.page(paginator.num_pages)
    
    categories = Category.objects.all()

    context = {
        'featured_post': featured_post,
        'regular_posts': regular_posts,
        'categories': categories,
    }
    return render(request, 'home.html', context)

def posts_by_category(request, category_id):
    # Fetch the posts based on the category_id
    posts = Blogs.objects.filter(status='published', category=category_id).select_related('category', 'author')
    
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('home')  # Redirect to home if category not found
    
    # Get all categories for navigation
    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'category': category,
        'categories': categories,
        'meta_title': category.meta_title if category.meta_title else f"{category.category_name} - Articles & Resources",
        'meta_description': category.meta_description if category.meta_description else f"Browse all articles about {category.category_name}. Find resources, tips, and insights.",
    }
    return render(request, 'posts_by_category.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(Blogs, slug=slug, status='published')
    categories = Category.objects.all()
    related_posts = Blogs.objects.filter(
        category=post.category, 
        status='published'
    ).exclude(id=post.id).order_by('-created_at')[:3]
    
    # Prepare meta data for SEO
    meta_title = post.meta_title if post.meta_title else post.title
    meta_description = post.meta_description if post.meta_description else post.short_description
    og_title = post.og_title if post.og_title else meta_title
    og_description = post.og_description if post.og_description else meta_description
    og_image = post.og_image if post.og_image else post.blog_image
    
    context = {
        'post': post,
        'categories': categories,
        'related_posts': related_posts,
        'meta_title': meta_title,
        'meta_description': meta_description,
        'og_title': og_title,
        'og_description': og_description,
        'og_image': og_image,
        'twitter_card_type': post.twitter_card_type,
        'twitter_site': post.twitter_site,
        'schema_type': post.schema_type,
        'focus_keyword': post.focus_keyword,
    }
    return render(request, 'blogs.html', context)

def search(request):
    keyword = request.GET.get('keyword', '')
    blogs = Blogs.objects.filter(
        Q(title__icontains=keyword) | 
        Q(short_description__icontains=keyword) | 
        Q(blog_body__icontains=keyword),
        status='published'
    ).select_related('category', 'author')
    
    categories = Category.objects.all()
    
    context = {
        'blogs': blogs,
        'categories': categories,
        'keyword': keyword,
        'meta_title': f"Search Results for '{keyword}'",
        'meta_description': f"Search results for '{keyword}' on our blog. Find articles, tips, and resources related to your search query.",
    }
    return render(request, 'search.html', context)