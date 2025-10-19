from django.shortcuts import render, redirect, get_object_or_404
from blogs.models import Category, Blogs
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from .forms import CategoryForm, BlogPostForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from .forms import AddUserForm, EditUserForm

# Helper function to check if user has admin permissions
def is_admin_user(user):
    return user.has_perm('blogs.add_category') or user.is_superuser

def has_category_permission(user):
    """Check if user has any category permission"""
    return (user.has_perm('blogs.add_category') or 
            user.has_perm('blogs.change_category') or 
            user.has_perm('blogs.delete_category'))

def has_blog_permission(user):
    """Check if user has any blog permission"""
    return (user.has_perm('blogs.add_blogs') or 
            user.has_perm('blogs.change_blogs') or 
            user.has_perm('blogs.delete_blogs'))

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

# CATEGORY VIEWS
@login_required
def categories(request):
    # Check if user has any category permissions
    if not has_category_permission(request.user):
        messages.error(request, "You don't have permission to access categories.")
        return redirect('dashboard')
    return render(request, 'dashboard/categories.html')

@login_required
@permission_required('blogs.add_category', raise_exception=False)
def add_categories(request):
    # If user doesn't have permission, redirect with message
    if not request.user.has_perm('blogs.add_category'):
        messages.error(request, "You don't have permission to add categories.")
        return redirect('categories')
    
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

@login_required
@permission_required('blogs.change_category', raise_exception=False)
def edit_categories(request, pk):
    # If user doesn't have permission, redirect with message
    if not request.user.has_perm('blogs.change_category'):
        messages.error(request, "You don't have permission to edit categories.")
        return redirect('categories')
    
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

@login_required
@permission_required('blogs.delete_category', raise_exception=False)
def delete_categories(request, pk):
    # If user doesn't have permission, redirect with message
    if not request.user.has_perm('blogs.delete_category'):
        messages.error(request, "You don't have permission to delete categories.")
        return redirect('categories')
    
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

# BLOG POST VIEWS
@login_required
def posts(request):
    # Check if user has any blog permissions
    if not has_blog_permission(request.user):
        messages.error(request, "You don't have permission to access posts.")
        return redirect('dashboard')
    
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
@permission_required('blogs.add_blogs', raise_exception=False)
def add_posts(request):
    # If user doesn't have permission, redirect with message
    if not request.user.has_perm('blogs.add_blogs'):
        messages.error(request, "You don't have permission to add posts.")
        return redirect('posts')
    
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
@permission_required('blogs.change_blogs', raise_exception=False)
def edit_posts(request, pk):
    # If user doesn't have permission, redirect with message
    if not request.user.has_perm('blogs.change_blogs'):
        messages.error(request, "You don't have permission to edit posts.")
        return redirect('posts')
    
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
@permission_required('blogs.delete_blogs', raise_exception=False)
def delete_posts(request, pk):
    # If user doesn't have permission, redirect with message
    if not request.user.has_perm('blogs.delete_blogs'):
        messages.error(request, "You don't have permission to delete posts.")
        return redirect('posts')
    
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

# USER MANAGEMENT VIEWS (Only for superusers/staff)
@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser, login_url='dashboard')
def users(request):
    users = User.objects.exclude(pk=None)
    context = {
        'users': users
    }
    return render(request, 'dashboard/users.html', context)

@login_required
@permission_required('auth.add_user', raise_exception=False)
def add_users(request):
    # If user doesn't have permission, redirect with message
    if not request.user.has_perm('auth.add_user'):
        messages.error(request, "You don't have permission to add users.")
        return redirect('users')
    
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('users')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddUserForm()
    
    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_users.html', context)

@login_required
@permission_required('auth.change_user', raise_exception=False)
def edit_user(request, pk):
    # If user doesn't have permission, redirect with message
    if not request.user.has_perm('auth.change_user'):
        messages.error(request, "You don't have permission to edit users.")
        return redirect('users')
    
    user_obj = get_object_or_404(User, pk=pk)

    # Prevent users from editing themselves to remove their own permissions
    if user_obj == request.user and not request.user.is_superuser:
        messages.error(request, "You cannot edit your own user account.")
        return redirect('users')

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user_obj.username}" updated successfully!')
            return redirect('users')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EditUserForm(instance=user_obj)

    context = {
        'form': form,
        'user_obj': user_obj,
    }
    return render(request, 'dashboard/edit_user.html', context)

@login_required
@permission_required('auth.delete_user', raise_exception=False)
def delete_user(request, pk):
    # If user doesn't have permission, redirect with message
    if not request.user.has_perm('auth.delete_user'):
        messages.error(request, "You don't have permission to delete users.")
        return redirect('users')
    
    user = get_object_or_404(User, pk=pk)
    
    # Prevent users from deleting themselves
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully!')
        return redirect('users')
    
    context = {
        'user': user
    }
    return render(request, 'dashboard/delete_user.html', context)