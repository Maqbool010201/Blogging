from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
import re

# Status choices as constants
STATUS_DRAFT = 'draft'
STATUS_PUBLISHED = 'published'
STATUS_CHOICES = (
    (STATUS_DRAFT, 'Draft'),
    (STATUS_PUBLISHED, 'Published'),
)

# Schema type choices
SCHEMA_ARTICLE = 'Article'
SCHEMA_BLOG_POST = 'BlogPosting'
SCHEMA_NEWS_ARTICLE = 'NewsArticle'
SCHEMA_TECH_ARTICLE = 'TechArticle'
SCHEMA_CHOICES = [
    (SCHEMA_ARTICLE, 'Article'),
    (SCHEMA_BLOG_POST, 'Blog Post'),
    (SCHEMA_NEWS_ARTICLE, 'News Article'),
    (SCHEMA_TECH_ARTICLE, 'Technical Article'),
]

# Twitter card choices
TWITTER_SUMMARY = 'summary'
TWITTER_SUMMARY_LARGE_IMAGE = 'summary_large_image'
TWITTER_CARD_CHOICES = [
    (TWITTER_SUMMARY, 'Summary'),
    (TWITTER_SUMMARY_LARGE_IMAGE, 'Summary Large Image'),
]


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True, verbose_name="Category Name")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    # SEO fields for category pages
    meta_title = models.CharField(max_length=70, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=300, blank=True, verbose_name="Meta Description")

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['category_name']
        indexes = [
            models.Index(fields=['category_name']),
        ]
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
        # Auto-generate meta fields if empty
        if not self.meta_title:
            self.meta_title = f"{self.category_name} - Articles & Resources"
        if not self.meta_description:
            self.meta_description = f"Browse all articles about {self.category_name}. Find resources, tips, and insights."
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('posts_by_category', kwargs={'category_id': self.id})
        
    def clean(self):
        # Validate meta title length
        if self.meta_title and len(self.meta_title) > 70:
            raise ValidationError({'meta_title': 'Meta title cannot exceed 70 characters.'})
        if self.meta_description and len(self.meta_description) > 300:
            raise ValidationError({'meta_description': 'Meta description cannot exceed 300 characters.'})


class Blogs(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="Title")
    slug = models.SlugField(unique=True, blank=True, max_length=110, verbose_name="Slug")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='blogs', verbose_name="Category")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Author")
    blog_image = models.ImageField(upload_to='uploads/%Y/%m/%d/', verbose_name="Blog Image")
    short_description = models.TextField(max_length=1000, verbose_name="Short Description")
    blog_body = models.TextField(max_length=5000, verbose_name="Blog Content")
    
    # Basic SEO fields
    meta_title = models.CharField(max_length=70, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(max_length=300, blank=True, verbose_name="Meta Description")
    focus_keyword = models.CharField(
        max_length=50, blank=True, 
        help_text="Primary keyword for this content",
        verbose_name="Focus Keyword"
    )
    
    # Open Graph fields for social media
    og_image = models.ImageField(
        upload_to='og_images/%Y/%m/%d/', 
        blank=True, 
        null=True,
        help_text="Open Graph image for social media sharing (1200×630px recommended)",
        verbose_name="OG Image"
    )
    og_title = models.CharField(
        max_length=90, blank=True, 
        help_text="Open Graph title for social media",
        verbose_name="OG Title"
    )
    og_description = models.TextField(
        max_length=300, blank=True, 
        help_text="Open Graph description for social media",
        verbose_name="OG Description"
    )
    
    # Twitter Card fields
    twitter_card_type = models.CharField(
        max_length=20,
        choices=TWITTER_CARD_CHOICES,
        default=TWITTER_SUMMARY_LARGE_IMAGE,
        help_text="Type of Twitter Card to use",
        verbose_name="Twitter Card Type"
    )
    twitter_site = models.CharField(
        max_length=15, 
        blank=True, 
        help_text="Twitter @username of the site (without @)",
        verbose_name="Twitter Site"
    )
    
    # Schema.org structured data
    schema_type = models.CharField(
        max_length=50,
        choices=SCHEMA_CHOICES,
        default=SCHEMA_BLOG_POST,
        help_text="Schema.org type for structured data",
        verbose_name="Schema Type"
    )
    
    status = models.CharField(
        max_length=100, choices=STATUS_CHOICES, default=STATUS_DRAFT,
        db_index=True, verbose_name="Status"
    )
    is_featured = models.BooleanField(default=False, db_index=True, verbose_name="Is Featured")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

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
        # Validate slug doesn't contain special characters
        if self.slug and not re.match(r'^[a-z0-9-]+$', self.slug):
            raise ValidationError({'slug': 'Slug can only contain lowercase letters, numbers, and hyphens.'})
        
        # Validate meta field lengths
        if self.meta_title and len(self.meta_title) > 70:
            raise ValidationError({'meta_title': 'Meta title cannot exceed 70 characters.'})
        if self.meta_description and len(self.meta_description) > 300:
            raise ValidationError({'meta_description': 'Meta description cannot exceed 300 characters.'})
        if self.og_title and len(self.og_title) > 90:
            raise ValidationError({'og_title': 'OG title cannot exceed 90 characters.'})
        if self.og_description and len(self.og_description) > 300:
            raise ValidationError({'og_description': 'OG description cannot exceed 300 characters.'})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            counter = 1
            # Ensure slug uniqueness
            while Blogs.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
                
        # Set meta fields if empty
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
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def get_related_posts(self, limit=3):
        """Get related posts from the same category"""
        return Blogs.objects.filter(
            category=self.category, 
            status=STATUS_PUBLISHED
        ).exclude(id=self.id).order_by('-created_at')[:limit]
    
    @property
    def estimated_reading_time(self):
        """Calculate estimated reading time in minutes"""
        words_per_minute = 200
        word_count = len(self.blog_body.split())
        return max(1, round(word_count / words_per_minute))