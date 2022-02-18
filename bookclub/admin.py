from django.contrib import admin
from bookclub.models import User, Club, Book , Rating, Meeting, Event


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""
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
    list_display = ["title", "club", "book", "time", "notes"]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for events."""
    list_display = [
        'type_of_actor', 'type_of_action', 'message', 'created_at',
    ]

    
    
