from django.contrib import admin
from .models import Category, Blogs
from django.utils.html import format_html
from django import forms

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'post_count', 'created_at', 'updated_at')
    search_fields = ('category_name',)
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    

class BlogAdminForm(forms.ModelForm):
    class Meta:
        model = Blogs
        fields = '__all__'

class BlogsAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    list_display = ('title', 'category', 'author', 'status', 'is_featured', 'created_at', 'updated_at', 'blog_image_preview')
    list_filter = ('category', 'status', 'is_featured', 'created_at', 'updated_at')
    search_fields = ('title', 'short_description', 'blog_body', 'category__category_name', 
                     'author__username', 'meta_title', 'meta_description', 'focus_keyword')
    list_editable = ('status', 'is_featured')
    readonly_fields = ('created_at', 'updated_at', 'blog_image_preview', 
                       'meta_title_preview', 'meta_description_preview')
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('blog_image', 'blog_image_preview', 'short_description', 'blog_body')
        }),
        ('SEO Meta Data', {
            'fields': ('meta_title', 'meta_description', 'focus_keyword'),
            'classes': ('collapse',)
        }),
        ('Open Graph (Social Media)', {
            'fields': ('og_image', 'og_title', 'og_description'),
            'classes': ('collapse',)
        }),
        ('Twitter Card', {
            'fields': ('twitter_card_type', 'twitter_site'),
            'classes': ('collapse',)
        }),
        ('Schema.org', {
            'fields': ('schema_type',),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('status', 'is_featured', 'created_at', 'updated_at')
        }),
    )
    
    def blog_image_preview(self, obj):
        if obj.blog_image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.blog_image.url)
        return "No Image"
    blog_image_preview.short_description = 'Image Preview'
    
    def meta_title_preview(self, obj):
        if obj.meta_title:
            return format_html('<span style="color: green;">{}</span> ({} characters)', 
                              obj.meta_title, len(obj.meta_title))
        return format_html('<span style="color: red;">Not set</span> - will use title')
    meta_title_preview.short_description = 'Meta Title Preview'
    
    def meta_description_preview(self, obj):
        if obj.meta_description:
            return format_html('<span style="color: green;">{}</span> ({} characters)', 
                              obj.meta_description, len(obj.meta_description))
        return format_html('<span style="color: red;">Not set</span> - will use short description')
    meta_description_preview.short_description = 'Meta Description Preview'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Check if the user has the global "view" permission for the Blogs model
        if request.user.has_perm('blogs.view_blogs'):
            return qs
        # If not, return only their own blogs
        return qs.filter(author=request.user)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # Make status and featured fields read-only for non-superusers
            form.base_fields['status'].disabled = True
            form.base_fields['is_featured'].disabled = True
        return form
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        
        # Auto-populate OG fields if empty
        if not obj.og_title and obj.meta_title:
            obj.og_title = obj.meta_title
        if not obj.og_description and obj.meta_description:
            obj.og_description = obj.meta_description
        if not obj.og_image and obj.blog_image:
            obj.og_image = obj.blog_image
        
        super().save_model(request, obj, form, change)
        
    # Custom admin action for publishing posts
    @admin.action(description='Publish selected posts')
    def make_published(self, request, queryset):
        queryset.update(status='published')
        
    # Custom admin action for featuring posts
    @admin.action(description='Feature selected posts')
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        
    # Custom admin action for unfeaturing posts
    @admin.action(description='Unfeature selected posts')
    def make_unfeatured(self, request, queryset):
        queryset.update(is_featured=False)
        
    actions = [make_published, make_featured, make_unfeatured]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Blogs, BlogsAdmin)