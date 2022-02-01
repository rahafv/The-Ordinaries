from django.core.management.base import BaseCommand
from bookclub.models import User, Club, Book

class Command(BaseCommand):

    def handle(self, *args, **options):
        User.objects.filter(is_staff=False).delete()
        Club.objects.all().delete()
        Book.objects.all().delete()
