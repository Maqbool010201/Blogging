# blogs/models.py
from django.db import models
from tinymce.models import HTMLField  # Import the HTMLField
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import re

# ---------------------------------------
# CONSTANTS
# ---------------------------------------
STATUS_DRAFT = 'draft'
STATUS_PUBLISHED = 'published'
STATUS_CHOICES = (
    (STATUS_DRAFT, 'Draft'),
    (STATUS_PUBLISHED, 'Published'),
)

SCHEMA_CHOICES = [
    ('Article', 'Article'),
    ('BlogPosting', 'Blog Post'),
    ('NewsArticle', 'News Article'),
    ('TechArticle', 'Technical Article'),
]

TWITTER_CARD_CHOICES = [
    ('summary', 'Summary'),
    ('summary_large_image', 'Summary Large Image'),
]

# ---------------------------------------
# CATEGORY MODEL
# ---------------------------------------
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True, verbose_name="Category Name")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    # SEO fields
    meta_title = models.CharField(max_length=70, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=300, blank=True, verbose_name="Meta Description")

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['category_name']
        indexes = [models.Index(fields=['category_name'])]
        permissions = [
            ("can_publish", "Can publish post"),
            ("can_feature", "Can feature post"),
        ]

    def __str__(self):
        return self.category_name

    @property
    def post_count(self):
        return self.blogs.filter(status=STATUS_PUBLISHED).count()
    
    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.category_name} - Articles & Insights"
        if not self.meta_description:
            self.meta_description = f"Browse the latest articles and insights about {self.category_name}."
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('posts_by_category', kwargs={'category_id': self.id})
        
    def clean(self):
        if self.meta_title and len(self.meta_title) > 70:
            raise ValidationError({'meta_title': 'Meta title cannot exceed 70 characters.'})
        if self.meta_description and len(self.meta_description) > 300:
            raise ValidationError({'meta_description': 'Meta description cannot exceed 300 characters.'})

# ---------------------------------------
# BLOGS MODEL
# ---------------------------------------
class Blogs(models.Model):
    # Basic info
    title = models.CharField(max_length=200, unique=True, verbose_name="Title")
    slug = models.SlugField(max_length=110, unique=True, blank=True, verbose_name="Slug")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs', verbose_name="Category")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Author")

    # Main content - CHANGED THIS FIELD
    short_description = models.TextField(max_length=1000, verbose_name="Short Description")
    blog_body = HTMLField(max_length=10000, verbose_name="Blog Content")  # Changed from TextField to HTMLField
    blog_image = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True, verbose_name="Blog Image")

    # SEO fields
    meta_title = models.CharField(max_length=70, blank=True, null=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=300, blank=True, null=True, verbose_name="Meta Description")
    focus_keyword = models.CharField(max_length=50, blank=True, help_text="Primary keyword for SEO", verbose_name="Focus Keyword")

    # Canonical + multilingual support
    canonical_url = models.URLField(blank=True, null=True, help_text=_("Override the default canonical URL"))
    language = models.CharField(max_length=10, default='en', help_text=_("Language code (e.g. en, ar, fr)"))
    parent_blog = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='translations', help_text=_("Link to original post for translations"))

    # Social media (Open Graph)
    og_image = models.ImageField(upload_to='og_images/%Y/%m/%d/', blank=True, null=True, verbose_name="OG Image", help_text="1200×630px recommended")
    og_title = models.CharField(max_length=90, blank=True, verbose_name="OG Title")
    og_description = models.TextField(max_length=300, blank=True, verbose_name="OG Description")

    # Twitter
    twitter_card_type = models.CharField(max_length=20, choices=TWITTER_CARD_CHOICES, default='summary_large_image', verbose_name="Twitter Card Type")
    twitter_site = models.CharField(max_length=15, blank=True, verbose_name="Twitter Site", help_text="Twitter username without @")

    # Schema.org
    schema_type = models.CharField(max_length=50, choices=SCHEMA_CHOICES, default='BlogPosting', verbose_name="Schema Type")

    # Visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True, verbose_name="Status")
    is_featured = models.BooleanField(default=False, db_index=True, verbose_name="Featured")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured', 'created_at']),
            models.Index(fields=['slug', 'status']),
            models.Index(fields=['category', 'status', 'created_at']),
        ]
        permissions = [
            ("can_publish", "Can publish blog post"),
            ("can_feature", "Can feature blog post"),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.slug and not re.match(r'^[a-z0-9-]+$', self.slug):
            raise ValidationError({'slug': 'Slug can only contain lowercase letters, numbers, and hyphens.'})
        if self.meta_title and len(self.meta_title) > 70:
            raise ValidationError({'meta_title': 'Meta title cannot exceed 70 characters.'})
        if self.meta_description and len(self.meta_description) > 300:
            raise ValidationError({'meta_description': 'Meta description cannot exceed 300 characters.'})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            counter = 1
            while Blogs.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        if not self.meta_title:
            self.meta_title = self.title[:70]
        if not self.meta_description:
            self.meta_description = self.short_description[:300]
        if not self.og_title:
            self.og_title = self.meta_title
        if not self.og_description:
            self.og_description = self.meta_description
        if not self.og_image and self.blog_image:
            self.og_image = self.blog_image
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.pk and self.slug:
            return reverse('blog_detail', kwargs={'slug': self.slug})

    def get_canonical_url(self):
        if self.canonical_url:
            return self.canonical_url
        if self.parent_blog:
            return self.parent_blog.get_absolute_url()
        return self.get_absolute_url()

    def get_related_posts(self, limit=3):
        return Blogs.objects.filter(
            category=self.category, status=STATUS_PUBLISHED
        ).exclude(id=self.id).order_by('-created_at')[:limit]

    @property
    def estimated_reading_time(self):
        # Update this method to handle HTML content properly
        # Remove HTML tags for accurate word count
        import re
        clean_text = re.sub('<[^<]+?>', '', self.blog_body)
        word_count = len(clean_text.split())
        words_per_minute = 200
        return max(1, round(word_count / words_per_minute))

# ---------------------------------------
# COMMENT MODEL
# ---------------------------------------
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blogs, on_delete=models.CASCADE)
    comment = models.TextField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.comment[:40]}"

# ---------------------------------------
# ADVERTISEMENT MODEL
class Advertisement(models.Model):
    AD_TYPE_CHOICES = [
        ('GOOGLE_ADSENSE', 'Google AdSense'),
        ('AFFILIATE', 'Affiliate Ad'),
        ('CUSTOM', 'Custom Code'),
        ('BANNER', 'Image Banner'),
        ('VIDEO_IN_STREAM', 'Video In-Stream'),
        ('VIDEO_OUT_STREAM', 'Video Out-Stream'),
        ('BUMPER', 'Bumper Ad'),
    ]
    PLACEMENT_CHOICES = [
        ('HEADER', 'Header'),
        ('SIDEBAR_TOP', 'Sidebar Top'),
        ('SIDEBAR_BOTTOM', 'Sidebar Bottom'),
        ('CONTENT_TOP', 'Content Top'),
        ('CONTENT_MIDDLE', 'Content Middle'),
        ('CONTENT_BOTTOM', 'Content Bottom'),
        ('CONTENT_VIDEO', 'Content Video'),
        ('FOOTER', 'Footer'),
    ]
    
    DISPLAY_STRATEGY_CHOICES = [
        ('RANDOM', 'Random Rotation'),
        ('WEIGHTED', 'Weighted by Priority'),
        ('SEQUENTIAL', 'Sequential Display'),
        ('CATEGORY_MATCH', 'Match Post Category'),
    ]

    name = models.CharField(max_length=100, help_text="Descriptive name for this ad")
    ad_type = models.CharField(max_length=20, choices=AD_TYPE_CHOICES, default='CUSTOM')
    is_active = models.BooleanField(default=True, verbose_name="Ad Active")
    placement_area = models.CharField(max_length=20, choices=PLACEMENT_CHOICES, default='SIDEBAR_TOP')
    
    # New fields for better targeting
    display_strategy = models.CharField(
        max_length=20, 
        choices=DISPLAY_STRATEGY_CHOICES, 
        default='RANDOM',
        help_text="How this ad should be selected for display"
    )
    target_categories = models.ManyToManyField(
        'Category', 
        blank=True,
        help_text="Only show this ad for posts in these categories (leave empty for all categories)"
    )
    max_display_count = models.PositiveIntegerField(
        default=0,
        help_text="Maximum times to display this ad (0 = unlimited)"
    )
    
    ad_code = models.TextField(blank=True, help_text="Paste AdSense or custom HTML code")
    image = models.ImageField(upload_to='ads/', blank=True, null=True, help_text="For image banner ads")
    destination_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    priority = models.IntegerField(default=1, help_text="Higher number = higher priority")
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = "Advertisement"
        verbose_name_plural = "Advertisements"

    def __str__(self):
        return f"{self.name} ({self.get_ad_type_display()})"

    def is_currently_active(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        if self.max_display_count > 0 and self.impressions >= self.max_display_count:
            return False
        return True

    def should_display_for_category(self, category_id):
        """Check if this ad should be displayed for a specific category"""
        if not self.target_categories.exists():
            return True
        return self.target_categories.filter(id=category_id).exists()

# LEGAL PAGES, CONTACT, WRITE-FOR-US
# ---------------------------------------
class LegalPage(models.Model):
    PAGE_TYPES = [
        ('PRIVACY', 'Privacy Policy'),
        ('TERMS', 'Terms of Service'),
        ('COOKIE', 'Cookie Policy'),
        ('DISCLAIMER', 'Disclaimer'),
        ('ABOUT', 'About Us'),
    ]
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.get_page_type_display()

class ContactSubmission(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('BUSINESS', 'Business Inquiry'),
        ('GENERAL', 'General Question'),
        ('TECHNICAL', 'Technical Support'),
        ('OTHER', 'Other'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES, default='GENERAL')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class WriteForUsSubmission(models.Model):
    WRITING_CATEGORY_CHOICES = [
        ('TECH', 'Technology'),
        ('BUSINESS', 'Business'),
        ('LIFESTYLE', 'Lifestyle'),
        ('HEALTH', 'Health & Wellness'),
        ('TRAVEL', 'Travel'),
        ('FOOD', 'Food & Cooking'),
        ('OTHER', 'Other'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    writing_category = models.CharField(max_length=20, choices=WRITING_CATEGORY_CHOICES, default='TECH')
    topic = models.CharField(max_length=200)
    writing_experience = models.TextField(blank=True)
    portfolio_link = models.URLField(blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.topic}"
    

class NewsletterSubscriber(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email
    
class SocialMedia(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('pinterest', 'Pinterest'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, unique=True)
    url = models.URLField(help_text="Full URL to your social media profile")
    icon_class = models.CharField(
        max_length=50, 
        default="fab fa-",
        help_text="FontAwesome icon class (e.g., fab fa-facebook-f)"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        verbose_name = "Social Media Link"
        verbose_name_plural = "Social Media Links"
        ordering = ['order', 'platform']
    
    def __str__(self):
        return f"{self.get_platform_display()} - {self.url}"
    
    def get_icon_class(self):
        """Get the proper icon class for the platform"""
        if self.icon_class and self.icon_class != "fab fa-":
            return self.icon_class
        
        # Default icons if not specified
        icon_map = {
            'facebook': 'fab fa-facebook-f',
            'twitter': 'fab fa-twitter',
            'instagram': 'fab fa-instagram',
            'linkedin': 'fab fa-linkedin-in',
            'pinterest': 'fab fa-pinterest',
            'youtube': 'fab fa-youtube',
            'tiktok': 'fab fa-tiktok',
            'whatsapp': 'fab fa-whatsapp',
            'telegram': 'fab fa-telegram',
        }
        return icon_map.get(self.platform, 'fab fa-link')    
