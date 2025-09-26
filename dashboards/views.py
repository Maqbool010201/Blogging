from django.shortcuts import render, redirect, get_object_or_404
from blogs.models import Category, Blogs
from django.contrib.auth.decorators import login_required
from .forms import CategoryForm, BlogPostForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required(login_url='login')
def dashboard(request):
    # Get counts for CURRENT USER only
    category_count = Category.objects.filter(blogs__author=request.user).distinct().count()
    blogs_count = Blogs.objects.filter(author=request.user).count()
    
    # Get querysets for CURRENT USER only
    user_categories = Category.objects.filter(blogs__author=request.user).distinct()
    user_recent_posts = Blogs.objects.filter(author=request.user).order_by('-created_at')[:5]

    context = {
        'category_count': category_count,
        'blogs_count': blogs_count,
        'categories': user_categories,
        'recent_posts': user_recent_posts,
    }
    return render(request, 'dashboard/dashboard.html', context)

def categories(request):
    return render(request, 'dashboard/categories.html') 

def add_categories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    context = {
        'form': form
    }
    return render(request, 'dashboard/add_categories.html', context)

def edit_categories(request, pk):
    try:
        category = Category.objects.get(id=pk)
    except Category.DoesNotExist:
        return render(request, 'dashboard/error.html', {
            'error_title': 'Category Not Found',
            'error_message': 'The category you are trying to edit does not exist.',
            'redirect_url': 'categories'
        }, status=404)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category
    }
    return render(request, 'dashboard/edit_categories.html', context)

def delete_categories(request, pk):
    try:
        category = Category.objects.get(id=pk)
    except Category.DoesNotExist:
        return render(request, 'dashboard/error.html', {
            'error_title': 'Category Not Found',
            'error_message': 'The category you are trying to delete does not exist.',
            'redirect_url': 'categories'
        }, status=404)
    
    if request.method == 'POST':
        category_name = category.category_name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('categories')
    
    context = {
        'category': category
    }
    return render(request, 'dashboard/delete_categories.html', context)

@login_required(login_url='login')
def posts(request):
    # Get all posts for the current user for counting
    all_posts = Blogs.objects.filter(author=request.user)
    
    # Get counts for stats from all posts
    published_count = all_posts.filter(status='published').count()
    draft_count = all_posts.filter(status='draft').count()
    featured_count = all_posts.filter(is_featured=True).count()
    
    # Create paginated queryset for display (ordered by latest first)
    posts_list = all_posts.order_by('-created_at')
    paginator = Paginator(posts_list, 10)  # Show 10 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'published_count': published_count,
        'draft_count': draft_count,
        'featured_count': featured_count,
    }
    return render(request, 'dashboard/posts.html', context)

@login_required
def add_posts(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            # Create but don't save yet
            post = form.save(commit=False)
            # Set the author to current user
            post.author = request.user
            # Save the post
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('posts')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm()
    
    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_posts.html', context)

@login_required
def edit_posts(request, pk):
    try:
        # Get the post, ensure it belongs to current user
        post = Blogs.objects.get(id=pk, author=request.user)
    except Blogs.DoesNotExist:
        # Show friendly error page instead of 404
        return render(request, 'dashboard/error.html', {
            'error_title': 'Post Not Found',
            'error_message': 'The post you are trying to edit does not exist or you do not have permission to edit it.',
            'redirect_url': 'posts'
        }, status=404)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('posts')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm(instance=post)
    
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'dashboard/edit_posts.html', context)

@login_required
def delete_posts(request, pk):
    try:
        # Get the post, ensure it belongs to current user
        post = Blogs.objects.get(id=pk, author=request.user)
    except Blogs.DoesNotExist:
        # Show friendly error page instead of 404
        return render(request, 'dashboard/error.html', {
            'error_title': 'Post Not Found',
            'error_message': 'The post you are trying to delete does not exist or you do not have permission to delete it.',
            'redirect_url': 'posts'
        }, status=404)
    
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Post "{post_title}" deleted successfully!')
        return redirect('posts')
    
    context = {
        'post': post
    }
    return render(request, 'dashboard/delete_posts.html', context)