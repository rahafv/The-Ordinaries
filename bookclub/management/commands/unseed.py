from django.core.management.base import BaseCommand
from bookclub.models import User, Club, Book, Rating

class Command(BaseCommand):

    def handle(self, *args, **options):
        self.emptyDatabase()

    def emptyDatabase(self):
        User.objects.filter(is_staff=False).delete()
        Club.objects.all().delete()
        Book.objects.all().delete()
        Rating.objects.all().delete()

unseed = Command()
