from django.shortcuts import render, redirect
from blogs.models import Category, Blogs
from .forms import SignUpForm
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import url_has_allowed_host_and_scheme

def home(request):
    categories = Category.objects.all()
    featured_post = Blogs.objects.filter(is_featured=True)
    regular_posts = Blogs.objects.filter(is_featured=False)[:6]
    
    context = {
        'categories': categories,
        'featured_post': featured_post,
        'regular_posts': regular_posts
    }
    return render(request, 'home.html', context)

def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register')
    else:
        form = SignUpForm()
    
    context = {'form': form}
    return render(request, 'register.html', context)

def login(request):
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            # 1. First, try to get the 'next' URL from the POST data (submitted by the form)
            next_url = request.POST.get('next')
            # 2. If it's not in POST, provide a default (e.g., 'dashboard')
            if not next_url:
                next_url = 'dashboard'

            # 3. (Important) Security check to prevent open redirects
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
                return redirect(next_url)
            else:
                return redirect('dashboard')  # Redirect to default if 'next' is unsafe
    else:
        form = AuthenticationForm()

    # For GET requests, pass the existing 'next' parameter to the template context
    context = {'form': form}
    return render(request, 'login.html', context)
def logout(request):
    auth.logout(request)
    return redirect('home')