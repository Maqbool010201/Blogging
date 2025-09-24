from django.shortcuts import render, redirect
from blogs.models import Category, Blogs
from django.contrib.auth.decorators import login_required
from .forms import CategoryForm

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