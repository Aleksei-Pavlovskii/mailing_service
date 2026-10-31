from django.contrib import admin

from users.models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "phone", "country", "is_active", "is_staff", "date_joined")