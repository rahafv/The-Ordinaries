import sys
from django.core.management.base import BaseCommand, CommandError

from bookclub.models import User, Club, Book 

from faker import Faker

import csv
from django.utils import timezone
import os
from .unseed import unseed

class Command(BaseCommand):
    USER_COUNT = 100
    POST_COUNT = 2000

    DEFAULT_PASSWORD = 'Password123'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        unseed.emptyDatabase()
        # start_time = timezone.now()
        #self.create_users()
        # end_time = timezone.now()
        # self.stdout.write(
        #     self.style.SUCCESS(
        #         f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
        #     )
        # )
        self.create_books()

    def create_users(self):

        MAX_USERS = 10000
        users_path = os.path.abspath("book-review-dataset/BX-Users.csv")
        with open(users_path, "r", encoding='latin-1') as csv_file:
            users_data = list(csv.reader(csv_file, delimiter=";"))

            users = []
            usernames = []
            ctr =1
            for row in users_data[1:]:
                # make them unique
              
                first_name = self.faker.first_name()
                last_name = self.faker.last_name()
                username = self.create_username(first_name, last_name)
                
                
                if username in usernames: 
                    username = username+ str(ctr)
                    ctr += 1

                usernames.append(username)

                user = User(
                    first_name = first_name,
                    last_name = last_name,
                    username = username,
                    email = self.create_email(username),
                    age = self.get_age(row[2]),
                    city = self.get_city(row[1]),
                    region = self.get_region(row[1]),
                    country = self.get_country(row[1]),
                    bio = self.faker.text(max_nb_chars=300),
                    password = Command.DEFAULT_PASSWORD,
                )

                users.append(user)

                if len(users) > MAX_USERS:
                    User.objects.bulk_create(users)
                    users = []
                    break

            if users:
                User.objects.bulk_create(users)

        

    def create_books(self):
        MAX_BOOKS = 20000
        books_path = os.path.abspath("book-review-dataset/BX_Books.csv")
        with open(books_path, "r", encoding='latin-1') as csv_file:
            books_data = list(csv.reader(csv_file, delimiter=","))

            books = []
            for col in books_data[1:]:
              
                print(col["test"])
                book = Book(
                    ISBN = col[4],
                    title = col[6],
                    author = col[1],
                    image_url = col[7],
                )

                books.append(book)

                if len(books) > MAX_BOOKS:
                    Book.objects.bulk_create(books)
                    books = []
                    break

            if books:
                Book.objects.bulk_create(books)




    def create_username(self, first_name, last_name):
        return first_name.lower() + last_name.lower()

    def create_email(self, username):
        return username + "@example.org"

    def get_age(self, age):
        try:
            return int(age)
        except:
            pass

    def get_city(self, location):
        try:
            return location.split(',')[0]
        except:
            pass

    def get_region(self, location):
        try:
            return location.split(',')[1]
        except:
            pass

    def get_country(self, location):
        try:
            return location.split(',')[2]
        except:
            pass



