from django.contrib import admin

# Register your models here.

from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff')

admin.site.register(CustomUser, CustomUserAdmin)