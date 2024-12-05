from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser

# Register your models here.


class UserAdmin(BaseUserAdmin):
    """Modifies the admin user display."""

    ordering = ("first_name", "last_name")


admin.site.register(CustomUser, UserAdmin)
