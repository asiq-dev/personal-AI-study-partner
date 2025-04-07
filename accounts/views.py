from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.forms import CustomUserCreationForm, UserLoginForm

# Create your views here.

# SignUp View
class SignUpView(CreateView):
    form_class = CustomUserCreationForm  # Custom user creation form
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('tutors_list')  # after signup redirect to chat home page


# Login View
class CustomLoginView(LoginView):
    form_class = UserLoginForm  # Use the default UserCreationForm for login
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('tutors_list')  # this requires overriding get_success_url()

    def get_success_url(self):
        return self.success_url

# Logout View
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')