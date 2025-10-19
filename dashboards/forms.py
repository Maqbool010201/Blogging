from django import forms
from blogs.models import Category, Blogs
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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



class AddUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 
                  'is_superuser', 'groups', 'user_permissions',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing user, make username read-only
        if self.instance and self.instance.pk:
            self.fields['username'].disabled = True



class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email', 'first_name', 'last_name', 'is_active', 'is_staff', 
                  'is_superuser', 'groups', 'user_permissions',)