# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Blogs, Category, Comment, LegalPage, Advertisement, NewsletterSubscriber
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .forms import ContactForm, WriteForUsForm 
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .utils.breadcrumbs import Breadcrumb  # Import Breadcrumb class

def home(request):
    # Featured posts (Hero + Featured Grid)
    featured_posts = Blogs.objects.filter(
        status='published', 
        is_featured=True
    ).select_related('category', 'author').order_by('-created_at')

    # Regular posts (paginated)
    regular_posts_qs = Blogs.objects.filter(
        status='published', 
        is_featured=False
    ).select_related('category', 'author').order_by('-created_at')

    paginator = Paginator(regular_posts_qs, 10)  # Show 10 posts per page
    page = request.GET.get('page')
    regular_posts = paginator.get_page(page)

    # Categories for sidebar
    categories = Category.objects.all()

    # Popular posts (based on views or created_at fallback)
    popular_posts = Blogs.objects.filter(status='published').order_by('-created_at')[:5]

    # Active advertisements
    now = timezone.now()
    sidebar_ads = Advertisement.objects.filter(
        placement_area__in=['SIDEBAR_TOP', 'SIDEBAR_BOTTOM'],
        is_active=True
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    ).order_by('-priority')

    content_ads = Advertisement.objects.filter(
        placement_area__in=['CONTENT_TOP', 'CONTENT_MIDDLE', 'CONTENT_BOTTOM'],
        is_active=True
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    ).order_by('-priority')

    # Set breadcrumbs for homepage
    request.breadcrumbs = [
        Breadcrumb('Home', '/', True)
    ]

    context = {
        'featured_post': featured_posts,   # Hero + Featured grid
        'regular_posts': regular_posts,    # Paginated regular posts
        'categories': categories,          # Sidebar categories
        'popular_posts': popular_posts,    # Popular posts section
        'sidebar_ads': sidebar_ads,        # Sidebar ads
        'content_ads': content_ads,        # Content ads
    }

    return render(request, 'home.html', context)

def category_list(request):
    # Get all categories
    categories = Category.objects.all()
    
    # If you want to add pagination for categories (optional)
    # paginator = Paginator(categories, 20)  # Show 20 categories per page
    # page = request.GET.get('page')
    # categories_page = paginator.get_page(page)
    
    # Set breadcrumbs for category list - EXACTLY like your blog_list view
    request.breadcrumbs = [
        Breadcrumb('Home', reverse('home')),
        Breadcrumb('Categories', None, True)
    ]

    context = {
        'categories': categories,
        # 'categories': categories_page,  # if using pagination
    }
    return render(request, 'blogs/category_list.html', context)

def posts_by_category(request, category_id):
    # Fetch the posts based on the category_id
    posts = Blogs.objects.filter(status='published', category=category_id).select_related('category', 'author')
    
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return redirect('home')  # Redirect to home if category not found
    
    # Get all categories for navigation
    categories = Category.objects.all()
    
    # Set breadcrumbs for category posts
    request.breadcrumbs = [
        Breadcrumb('Home', reverse('home')),
        Breadcrumb('Categories', reverse('category_list')),
        Breadcrumb(category.category_name, None, True)
    ]
    
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
    
    # comments
    if request.method == 'POST':
       comment = Comment()
       comment.user = request.user
       comment.blog = post
       comment.comment = request.POST['comment']
       comment.save()
       return HttpResponseRedirect(request.path_info)
    comments = Comment.objects.filter(blog=post)
    comments_count = comments.count()
    
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
    
    # Set breadcrumbs for blog detail
    request.breadcrumbs = [
        Breadcrumb('Home', reverse('home')),
        Breadcrumb('Blogs', reverse('blog_list')),
        Breadcrumb(post.title, None, True)
    ]
    
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
        'comments': comments,
        'comment_count': comments_count,
    }
    return render(request, 'blogs.html', context)

def blog_list(request):
    blogs = Blogs.objects.all().order_by('-created_at')  # or your field name
    paginator = Paginator(blogs, 10)  # show 10 blogs per page

    page = request.GET.get('page')
    blogs_page = paginator.get_page(page)
    
    # Set breadcrumbs for blog list
    request.breadcrumbs = [
        Breadcrumb('Home', reverse('home')),
        Breadcrumb('Blogs', None, True)
    ]

    context = {
        'blogs': blogs_page,
    }
    return render(request, 'blogs/blog_list.html', context)

def search(request):
    keyword = request.GET.get('keyword', '')
    blogs = Blogs.objects.filter(
        Q(title__icontains=keyword) | 
        Q(short_description__icontains=keyword) | 
        Q(blog_body__icontains=keyword),
        status='published'
    ).select_related('category', 'author')
    
    categories = Category.objects.all()
    
    # Set breadcrumbs for search results
    request.breadcrumbs = [
        Breadcrumb('Home', reverse('home')),
        Breadcrumb('Search Results', None, True)
    ]
    
    context = {
        'blogs': blogs,
        'categories': categories,
        'keyword': keyword,
        'meta_title': f"Search Results for '{keyword}'",
        'meta_description': f"Search results for '{keyword}' on our blog. Find articles, tips, and resources related to your search query.",
    }
    return render(request, 'search.html', context)

# Advertisement tracking views
@require_POST
@csrf_exempt
def record_ad_impression(request, ad_id):
    """Record ad impression"""
    try:
        ad = Advertisement.objects.get(id=ad_id)
        ad.impressions += 1
        ad.save()
        return JsonResponse({'status': 'success', 'ad_id': ad_id})
    except Advertisement.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Ad not found'}, status=404)

@require_POST
@csrf_exempt
def record_ad_click(request, ad_id):
    """Record ad click"""
    try:
        ad = Advertisement.objects.get(id=ad_id)
        ad.clicks += 1
        ad.save()
        return JsonResponse({'status': 'success', 'ad_id': ad_id})
    except Advertisement.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Ad not found'}, status=404)

# Legal Pages View - UPDATED
def legal_page_detail(request, page_type):
    """
    View for displaying legal pages with proper meta titles and breadcrumbs
    """
    legal_page = get_object_or_404(
        LegalPage, 
        page_type=page_type, 
        is_published=True
    )
    
    # Set meta title for template
    meta_title = f"{legal_page.title} - Your Blog Name"
    
    # Set breadcrumbs for legal pages
    request.breadcrumbs = [
        Breadcrumb('Home', reverse('home')),
        Breadcrumb(legal_page.title, None, True)
    ]
    
    context = {
        'page': legal_page,
        'meta_title': meta_title,
    }
    return render(request, 'blogs/legal_page.html', context)

# Contact Us View - UPDATED
def contact_us(request):
    """
    Contact form view with meta title and breadcrumbs
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact_us')
    else:
        form = ContactForm()

    # Set breadcrumbs for contact page
    request.breadcrumbs = [
        Breadcrumb('Home', reverse('home')),
        Breadcrumb('Contact Us', None, True)
    ]

    context = {
        'form': form,
        'meta_title': 'Contact Us - Your Blog Name'
    }
    return render(request, 'blogs/contact.html', context)

# Write for Us View - UPDATED  
def write_for_us(request):
    """
    View to handle 'Write for Us' submissions with meta title and breadcrumbs
    """
    if request.method == 'POST':
        form = WriteForUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your submission! We will review your proposal and get back to you soon.')
            return redirect('write_for_us')
    else:
        form = WriteForUsForm()

    # Set breadcrumbs for write for us page
    request.breadcrumbs = [
        Breadcrumb('Home', reverse('home')),
        Breadcrumb('Write for Us', None, True)
    ]

    context = {
        'form': form,
        'meta_title': 'Write for Us - Your Blog Name'
    }
    return render(request, 'blogs/write_for_us.html', context)


# Utility: Get Latest Posts
# ---------------------------
def get_latest_posts(limit=3):
    """Return latest published blog posts."""
    try:
        return Blogs.objects.filter(status='published').order_by('-created_at')[:limit]
    except Exception:
        return []


# ---------------------------
# Subscribe Newsletter (AJAX)
# ---------------------------
@csrf_exempt  # Remove this if you’re using {% csrf_token %} in your form
def subscribe_newsletter(request):
    """
    Handle newsletter subscription from frontend.
    Sends welcome email with recent posts.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request.'})

    email = request.POST.get('email', '').strip()
    name = request.POST.get('name', '').strip() or 'Subscriber'

    if not email:
        return JsonResponse({'success': False, 'message': 'Email is required.'})

    # Check existing subscriber
    if NewsletterSubscriber.objects.filter(email__iexact=email).exists():
        return JsonResponse({'success': False, 'message': 'You are already subscribed.'})

    # Create new subscriber
    subscriber = NewsletterSubscriber.objects.create(name=name, email=email)

    # Prepare context for welcome email
    context = {
        'name': name,
        'email': email,
        'site_name': getattr(settings, 'SITE_NAME', 'My Blog'),
        'domain': getattr(settings, 'DOMAIN', 'http://127.0.0.1:8000/'),
        'latest_posts': get_latest_posts(3),
        'now': timezone.now(),
    }

    subject = f"Welcome to {context['site_name']}"
    text_body = render_to_string('newsletter/welcome_email.txt', context)
    html_body = render_to_string('newsletter/welcome_email.html', context)

    # Build email message
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    msg.attach_alternative(html_body, "text/html")

    try:
        msg.send(fail_silently=False)
    except Exception as e:
        print("Failed to send welcome email:", e)

    return JsonResponse({'success': True, 'message': 'Thank you for subscribing! Check your email.'})


# ---------------------------
# Send Custom Newsletter (Admin-only endpoint)
# ---------------------------
@csrf_exempt  # Remove if using admin form with CSRF
def send_custom_newsletter(request):
    """
    Admin-only endpoint to send a custom newsletter
    with subject and message to all subscribers.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request.'})

    # Security check: Only admin/staff
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()

    if not subject or not message:
        return JsonResponse({'success': False, 'message': 'Subject and message are required.'})

    subscribers = list(NewsletterSubscriber.objects.values_list('email', flat=True))
    if not subscribers:
        return JsonResponse({'success': False, 'message': 'No subscribers found.'})

    context = {
        'subject': subject,
        'message': message,
        'site_name': getattr(settings, 'SITE_NAME', 'My Blog'),
        'domain': getattr(settings, 'DOMAIN', 'http://127.0.0.1:8000/'),
        'now': timezone.now(),
    }

    text_body = render_to_string('newsletter/custom_newsletter.txt', context)
    html_body = render_to_string('newsletter/custom_newsletter.html', context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.DEFAULT_FROM_EMAIL],  # send copy to yourself
        bcc=subscribers,  # main send list
    )
    msg.attach_alternative(html_body, "text/html")

    try:
        msg.send(fail_silently=False)
        return JsonResponse({'success': True, 'message': f'Newsletter sent to {len(subscribers)} subscribers.'})
    except Exception as e:
        print("Failed to send newsletter:", e)
        return JsonResponse({'success': False, 'message': f'Error sending newsletter: {e}'})