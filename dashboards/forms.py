from django import forms
from blogs.models import Category, Blogs

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'            


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = Blogs
        fields = ['title', 'category', 'blog_image', 'short_description', 
                  'blog_body', 'status', 'is_featured', 'meta_title', 
                  'meta_description', 'focus_keyword']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'blog_body':
                field.widget.attrs['rows'] = 8
            if field_name == 'short_description':
                field.widget.attrs['rows'] = 4
