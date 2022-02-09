from django.contrib import admin
from bookclub.models import User, Club, Book , Rating


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name"]

@admin.register(Club)
class UserAdmin(admin.ModelAdmin):
    list_display = ["name", "theme", "owner", "meeting_type"]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["ISBN", "title", "author"]

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["user_id", "book_id", "review", "rating", "created_at"]
    readonly_fields = ['created_at']