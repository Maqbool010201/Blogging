from django.shortcuts import render, redirect, get_object_or_404
from blogs.models import Category, Blogs
from django.contrib.auth.decorators import login_required
from .forms import CategoryForm, BlogPostForm
from django.contrib import messages


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
            return redirect('categories')
    form = CategoryForm()
    context = {
        'form': form
        }
    return render(request, 'dashboard/add_categories.html', context)


def edit_categories(request, pk):
    category = Category.objects.get(id=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = CategoryForm(instance=category)
    context = {
        'form': form
        }
    return render(request, 'dashboard/edit_categories.html', context)



def delete_categories(request, pk):
    category = Category.objects.get(id=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('categories')
    context = {
        'category': category
    }
    return render(request, 'dashboard/delete_categories.html', context)



def posts(request):
    posts = Blogs.objects.all()
    context = {
        'posts': posts
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
    
    # Get categories for the dropdown
    categories = Category.objects.all()
    
    context = {
        'form': form,
        'categories': categories
    }
    return render(request, 'dashboard/add_posts.html', context)

@login_required
def edit_posts(request, pk):
    # Get the post, ensure it belongs to current user
    post = get_object_or_404(Blogs, id=pk, author=request.user)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('posts')
    else:
        form = BlogPostForm(instance=post)
    
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'dashboard/edit_posts.html', context)

@login_required
def delete_posts(request, pk):
    # Get the post, ensure it belongs to current user
    post = get_object_or_404(Blogs, id=pk, author=request.user)
    
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Post "{post_title}" deleted successfully!')
        return redirect('posts')
    
    context = {
        'post': post
    }
    return render(request, 'dashboard/delete_posts.html', context)