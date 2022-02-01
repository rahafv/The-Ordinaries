from django.core.management.base import BaseCommand, CommandError

from bookclub.models import User, Club, Book

from faker import Faker

import csv
from django.utils import timezone
import os


class Command(BaseCommand):
    USER_COUNT = 100
    POST_COUNT = 2000

    DEFAULT_PASSWORD = 'Password123'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        # self.create_users()
        self.create_books()

    def create_users(self):
        start_time = timezone.now()

        MAX_USERS = 80000
        users_path = os.path.abspath("book-review-dataset/BX-Users.csv")
        with open(users_path, "r", encoding='latin-1') as csv_file:
            users_data = list(csv.reader(csv_file, delimiter=";"))

            users = []
            for row in users_data[1:]:
                # make them unique
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                for user in users:
                    if user.first_name == first_name:
                        first_name = self.faker.first_name()
                        last_name = self.faker.last_name()

                user = User(
                    first_name = first_name,
                    last_name = last_name,
                    username = create_username(first_name, last_name),
                    email = create_email(first_name, last_name),
                    age = get_age(row[2]),
                    city = get_city(row[1]),
                    region = get_region(row[1]),
                    country = get_country(row[1]),
                    bio = self.faker.text(max_nb_chars=300),
                    password = Command.DEFAULT_PASSWORD,
                )

                users.append(user)

                if len(users) > MAX_USERS:
                    User.objects.bulk_create(users)
                    users = []

            if users:
                User.objects.bulk_create(users)

        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )

    def create_books(self):
        start_time = timezone.now()

        MAX_BOOKS = 80000
        books_path = os.path.abspath("book-review-dataset/BX_Books.csv")
        with open(books_path, "r", encoding='latin-1') as csv_file:
            books_data = list(csv.reader(csv_file, delimiter=";"))

            books = []
            for col in books_data[1:]:
              
                book = Book(
                    ISBN = col[0],
                    title = col[1],
                    author = col[2],
                    publisher = col[4],
                    image_url = col[7],
                    year = col[3],
                )

                books.append(book)

                if len(books) > MAX_BOOKS:
                    try:
                        Book.objects.bulk_create(books)
                        books = []
                    except:
                        pass

            if books:
                try:
                    Book.objects.bulk_create(books)
                except:
                    pass

        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )


    def create_username(first_name, last_name):
        return first_name.lower() + last_name.lower()

    def create_email(first_name, last_name):
        return first_name + '.' + last_name + '@example.org'

    def get_age(age):
        try:
            return int(age)
        except:
            pass

    def get_city(location):
        try:
            return location.split(',')[0]
        except:
            pass

    def get_region(location):
        try:
            return location.split(',')[1]
        except:
            pass

    def get_country(location):
        try:
            return location.split(',')[2]
        except:
            pass


