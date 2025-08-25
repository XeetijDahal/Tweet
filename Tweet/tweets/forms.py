from django import forms
from .models import Tweet,Comment
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth.models import User
from multiselectfield import MultiSelectFormField



class UserRegistrationForm(UserCreationForm):
    TOPIC_CHOICES = (
        ('anime', 'Anime'),
        ('study', 'Study'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('nature', 'Nature'),
        ('beauty', 'Beauty'),
        # Add more if needed
    )

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Choose a username'
    }))
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))
    
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))

    # Add gener field (not part of User model)
    gener = MultiSelectFormField(choices=TOPIC_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['text', 'photo', 'title', 'gener']  # include all your fields here
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': "What's happening?"
            }),
            'title': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter the title...'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
        help_texts = {
            'photo': 'Optional. Upload an image for your tweet.',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your comment...'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter current password',
        'autocomplete': 'current-password',
    }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password',
        'autocomplete': 'new-password',
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm new password',
        'autocomplete': 'new-password',
    }))
