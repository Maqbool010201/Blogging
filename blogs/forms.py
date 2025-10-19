from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import ContactSubmission, WriteForUsSubmission

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'contact_type', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your message...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        
        self.helper.layout = Layout(
            Row(
                Column(Field('name', placeholder='Your full name'), css_class='mb-3')
            ),
            Row(
                Column(Field('email', placeholder='Your email address'), css_class='mb-3')
            ),
            Row(
                Column(Field('contact_type'), css_class='mb-3')
            ),
            Row(
                Column(Field('subject', placeholder='Subject of your message'), css_class='mb-3')
            ),
            Row(
                Column(Field('message'), css_class='mb-3')
            ),
            Row(
                Column(
                    Submit('submit', 'Send Message', css_class='btn-primary btn-lg w-100')
                )
            )
        )
        
        # Add Bootstrap styling to all fields
        for field_name, field in self.fields.items():
            if field_name != 'contact_type':  # Don't add form-control to select fields
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-select'

class WriteForUsForm(forms.ModelForm):
    class Meta:
        model = WriteForUsSubmission
        fields = ['name', 'email', 'writing_category', 'topic', 
                 'writing_experience', 'portfolio_link', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Tell us about your article idea...'}),
            'writing_experience': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Briefly describe your writing experience (optional)'}),
            'portfolio_link': forms.URLInput(attrs={'placeholder': 'https://your-portfolio.com (optional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        
        self.helper.layout = Layout(
            Row(
                Column(Field('name', placeholder='Your full name'), css_class='mb-3')
            ),
            Row(
                Column(Field('email', placeholder='Your email address'), css_class='mb-3')
            ),
            Row(
                Column(Field('writing_category'), css_class='mb-3')
            ),
            Row(
                Column(Field('topic', placeholder='What topic would you like to write about?'), css_class='mb-3')
            ),
            Row(
                Column(Field('writing_experience'), css_class='mb-3')
            ),
            Row(
                Column(Field('portfolio_link'), css_class='mb-3')
            ),
            Row(
                Column(Field('message'), css_class='mb-3')
            ),
            Row(
                Column(
                    Submit('submit', 'Submit Proposal', css_class='btn-primary btn-lg w-100')
                )
            )
        )
        
        # Add Bootstrap styling to all fields
        for field_name, field in self.fields.items():
            if field_name in ['writing_category']:  # Select fields
                field.widget.attrs['class'] = 'form-select'
            else:  # Input and textarea fields
                field.widget.attrs['class'] = 'form-control'


