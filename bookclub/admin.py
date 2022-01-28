from django.contrib import admin
from bookclub.models import User, Club

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name"]

@admin.register(Club)
class UserAdmin(admin.ModelAdmin):
    list_display = ["name", "theme", "owner", "meeting_type"]
