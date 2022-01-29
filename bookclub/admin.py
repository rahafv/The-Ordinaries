from django.contrib import admin
from bookclub.models import User, Book

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "first_name", "last_name"]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["ISBN", "title", "author", "publisher", "year"]
# Register your models here.
