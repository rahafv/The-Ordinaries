from django.contrib import admin
from bookclub.models import User, Club, Book , Rating, Meeting


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name"]

@admin.register(Club)
class UserAdmin(admin.ModelAdmin):
    list_display = ["name", "theme", "owner"]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["ISBN", "title", "author", "publisher", "year"]

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["user_id", "book_id", "review", "rating", "created_at"]
    readonly_fields = ['created_at']

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ["title", "club", "time", "notes"]