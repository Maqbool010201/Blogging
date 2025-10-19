# blogs/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django import forms
from django.urls import path, reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import (
    Category, Blogs, Comment, Advertisement,
    LegalPage, ContactSubmission, WriteForUsSubmission, NewsletterSubscriber, SocialMedia
)

# -------------------------------
# CATEGORY ADMIN
# -------------------------------


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'post_count', 'created_at', 'updated_at')
    search_fields = ('category_name',)
    readonly_fields = ('post_count', 'created_at', 'updated_at')

# -------------------------------
# COMMENT INLINE
# -------------------------------


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('user', 'comment', 'created_at', 'updated_at')
    can_delete = False

# -------------------------------
# BLOGS ADMIN
# -------------------------------
# -------------------------------
# BLOGS ADMIN
# -------------------------------


@admin.register(Blogs)
class BlogsAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'title',
        'category',
        'author',
        'status',
        'is_featured',
        'created_at',
        'updated_at',
        'estimated_reading_time'
    )
    list_display_links = ('image_thumbnail', 'title')
    list_filter = ('status', 'is_featured', 'category', 'author', 'created_at')
    search_fields = ('title', 'short_description', 'blog_body',
                     'meta_title', 'meta_description')
    readonly_fields = (
        'created_at', 'updated_at', 'estimated_reading_time',
        'get_canonical_url', 'og_image_preview', 'image_thumbnail'
    )
    list_editable = ('status', 'is_featured')
    prepopulated_fields = {'slug': ('title',)}  # ADD THIS LINE
    inlines = [CommentInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'category', 'author', 'short_description', 'blog_body', 'blog_image')
        }),
        ('SEO & Social', {
            'fields': ('meta_title', 'meta_description', 'focus_keyword',
                       'canonical_url', 'get_canonical_url',
                       'og_title', 'og_description', 'og_image', 'og_image_preview',
                       'twitter_card_type', 'twitter_site', 'schema_type')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'parent_blog', 'language')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    # ADD THIS METHOD TO FIX THE "View on site" ERROR
    def view_on_site(self, obj):
        """
        Override to prevent 'View on site' button from showing for unsaved objects
        """
        if obj.pk and obj.slug:  # Only show for saved objects with a slug
            from django.urls import reverse
            return reverse('blog_detail', kwargs={'slug': obj.slug})
        return None  # Hide the button for unsaved objects

    # NEW: Method to display image thumbnail in list view
    def image_thumbnail(self, obj):
        if obj.blog_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.blog_image.url
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #f8f9fa; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #6c757d; font-size: 10px;">No Image</div>'
        )
    image_thumbnail.short_description = 'Image'

    def estimated_reading_time(self, obj):
        return f"{obj.estimated_reading_time} min"
    estimated_reading_time.short_description = "Est. Reading Time"

    def get_canonical_url(self, obj):
        return obj.get_canonical_url()
    get_canonical_url.short_description = "Canonical URL"

    def og_image_preview(self, obj):
        if obj.og_image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.og_image.url)
        return "-"
    og_image_preview.short_description = "OG Image Preview"

# -------------------------------
# COMMENT ADMIN
# -------------------------------


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'short_comment',
                    'created_at', 'updated_at')
    search_fields = ('user__username', 'blog__title', 'comment')
    list_filter = ('created_at',)
    readonly_fields = ('user', 'blog', 'comment', 'created_at', 'updated_at')

    def short_comment(self, obj):
        return obj.comment[:50] + ('...' if len(obj.comment) > 50 else '')
    short_comment.short_description = "Comment"

# -------------------------------
# ADVERTISEMENT ADMIN
# -------------------------------


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('name', 'ad_type', 'placement_area', 'is_active', 'priority',
                    'start_date', 'end_date', 'is_currently_active', 'target_categories_list')
    list_filter = ('ad_type', 'placement_area',
                   'is_active', 'target_categories')
    search_fields = ('name', 'ad_code', 'alt_text')
    readonly_fields = ('created_at', 'updated_at',
                       'is_currently_active', 'impressions', 'clicks')
    list_editable = ('is_active', 'priority')
    filter_horizontal = ('target_categories',)  # Better for ManyToMany fields

    def target_categories_list(self, obj):
        return ", ".join([cat.category_name for cat in obj.target_categories.all()])
    target_categories_list.short_description = "Target Categories"

    def is_currently_active(self, obj):
        return obj.is_currently_active()
    is_currently_active.boolean = True
    is_currently_active.short_description = "Currently Active"

# -------------------------------
# LEGAL PAGE ADMIN
# -------------------------------


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_type', 'is_published', 'last_updated')
    list_filter = ('page_type', 'is_published')
    search_fields = ('title', 'content')
    readonly_fields = ('last_updated',)

# -------------------------------
# CONTACT SUBMISSION ADMIN
# -------------------------------


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'contact_type',
                    'is_resolved', 'submitted_at')
    list_filter = ('contact_type', 'is_resolved')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'submitted_at')
    list_editable = ('is_resolved',)

# -------------------------------
# WRITE-FOR-US SUBMISSION ADMIN
# -------------------------------


@admin.register(WriteForUsSubmission)
class WriteForUsSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'topic', 'writing_category',
                    'is_reviewed', 'submitted_at')
    list_filter = ('writing_category', 'is_reviewed')
    search_fields = ('name', 'email', 'topic', 'message')
    readonly_fields = ('name', 'email', 'topic', 'writing_experience',
                       'portfolio_link', 'message', 'submitted_at')
    list_editable = ('is_reviewed',)


# Crispy Form for sending newsletter
# -------------------------------
class CustomNewsletterForm(forms.Form):
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('send', 'Send Newsletter', css_class='btn btn-primary'))

# -------------------------------
# Newsletter Subscriber Admin
# -------------------------------


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subscribed_at')
    search_fields = ('name', 'email')

    # Add custom change list template to show Send Newsletter button
    change_list_template = "admin/newslettersubscriber_change_list.html"

    # Add custom URL for sending newsletter
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-newsletter/', self.admin_site.admin_view(self.send_newsletter),
                 name='send_newsletter'),
        ]
        return custom_urls + urls

    # View to send newsletter
    def send_newsletter(self, request):
        if request.method == 'POST':
            form = CustomNewsletterForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']

                subscribers = NewsletterSubscriber.objects.all()
                if not subscribers:
                    self.message_user(
                        request, "No subscribers found.", level='warning')
                    return redirect('admin:send_newsletter')

                context = {
                    'subject': subject,
                    'message': message,
                    'site_name': getattr(settings, 'SITE_NAME', 'My Blog'),
                    'domain': getattr(settings, 'DOMAIN', 'http://127.0.0.1:8000/'),
                }

                # Render email templates
                text_body = render_to_string(
                    'newsletter/custom_newsletter.txt', context)
                html_body = render_to_string(
                    'newsletter/custom_newsletter.html', context)

                emails = [sub.email for sub in subscribers]
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    bcc=emails
                )
                msg.attach_alternative(html_body, "text/html")

                try:
                    msg.send()
                    self.message_user(
                        request, f"Newsletter sent to {len(emails)} subscribers.")
                except Exception as e:
                    self.message_user(
                        request, f"Error sending newsletter: {e}", level='error')

                return redirect('..')
        else:
            form = CustomNewsletterForm()

        return render(request, 'admin/send_newsletter.html', {'form': form, 'title': 'Send Newsletter'})


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ['platform', 'url', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'platform']
    search_fields = ['platform', 'url']
    
    fieldsets = (
        ('Social Media Information', {
            'fields': ('platform', 'url', 'icon_class', 'is_active', 'order')
        }),
    )