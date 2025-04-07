# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'password1', 'password2')  # Added password fields
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded-lg',
                'placeholder': 'Enter your username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full p-2 border rounded-lg',
                'placeholder': 'Enter your email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full p-2 border rounded-lg',
                'placeholder': 'Enter your phone number',
            }),
            # Password fields are styled in __init__ because they're inherited
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the inherited password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full p-2 border rounded-lg',
            'placeholder': 'Enter your password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full p-2 border rounded-lg',
            'placeholder': 'Confirm your password',
        })
        # Remove help text for all fields
        for field_name, field in self.fields.items():
            field.help_text = ''

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full p-2 border rounded-lg',
            'placeholder': 'Enter your username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full p-2 border rounded-lg',
            'placeholder': 'Enter your password',
        })
        for field_name, field in self.fields.items():
            field.help_text = ''