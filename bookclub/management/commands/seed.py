import sys
from django.core.management.base import BaseCommand, CommandError
from bookclub.models import User, Club, Book , Rating
from faker import Faker
import csv
from django.utils import timezone
import time
import os
from .unseed import unseed
import random


class Command(BaseCommand):

    DEFAULT_PASSWORD = 'pbkdf2_sha256$260000$4BNvFuAWoTT1XVU8D6hCay$KqDCG+bHl8TwYcvA60SGhOMluAheVOnF1PMz0wClilc='

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        unseed.emptyDatabase()
        initial_start = time.time()
        start = time.time()
        self.create_users()
        self.users = User.objects.all()
        self.create_followers()

        end = time.time()
        print("users: ", end - start)

        start = time.time()
        self.create_clubs()
        end = time.time()
        print("club: ", end - start)

        start = time.time()
        self.populate_clubs()
        end = time.time()
        print("populating clubs: ", end - start)

        start = time.time()
        self.create_books()
        end = time.time()
        print("book: ", end - start)

        start = time.time()
        self.create_ratings()
        end = time.time()
        print("ratings: ", end - start)
        
        print("total time: ", end - initial_start)

    def create_users(self):

        MAX_USERS = 100
        users_path = os.path.abspath("book-review-dataset/Users.csv")
        with open(users_path, "r", encoding='latin-1') as csv_file:
            users_data = list(csv.reader(csv_file, delimiter=","))

            users = []
    
            for row in users_data[1:]:
                if row[10].isdigit():
                    age = int(row[10])
                else:
                    age = None

                user = User(
                    first_name = row[0],
                    last_name = row[1],
                    username = row[5],
                    email = row[5]+"@example.org",
                    age = age,
                    city = self.get_city(row[8]),
                    region = self.get_region(row[8]),
                    country = self.get_country(row[8]),
                    bio = row[4],
                    password = Command.DEFAULT_PASSWORD,
                    email_verified = True,
                )

                users.append(user)

                if len(users) > MAX_USERS:
                    User.objects.bulk_create(users)
                    users = []
                    break

            if users:
                User.objects.bulk_create(users)

    def create_followers(self):
        for user in self.users:
            self.create_followers_for_user(user)

    def create_followers_for_user(self, user):
        FOLLOW_PROBABILITY = 0.1

        for follower in self.users:
            if random.random() < FOLLOW_PROBABILITY:
                user.toggle_follow(follower)

    def create_clubs(self):
        MAX_CLUBS = 50
        clubs_path = os.path.abspath("book-review-dataset/Clubs.csv")
        with open(clubs_path, "r", encoding='latin-1') as csv_file:
            clubs_data = list(csv.reader(csv_file, delimiter=","))

            user_ids = list(self.users.values_list('id', flat=True))
        

            clubs = []
            for col in clubs_data[1:]:
                rand_id = random.randint(0, self.users.count()-1)

                TYPE_PROBABILITY = 0.1
                if random.random() < TYPE_PROBABILITY:
                    club_type = 'Private'
                else:
                    club_type = 'Public'
                
                club = Club(
                    name = col[4] + " club",
                    owner = User.objects.get(id = user_ids[rand_id]),
                    theme = col[1],
                    club_type = club_type,
                    city = col[2],
                    country = col[3],
                )


                clubs.append(club)

                if len(clubs) > MAX_CLUBS:
                    Club.objects.bulk_create(clubs)
                    clubs = []
                    break
                    

            if clubs:
                Club.objects.bulk_create(clubs)


    def create_books(self):
        MAX_BOOKS = 1000
        books_path = os.path.abspath("book-review-dataset/BX_Books.csv")
        with open(books_path, "r", encoding='latin-1') as csv_file:
            books_data = list(csv.reader(csv_file, delimiter=","))

            books = []
            for col in books_data[1:]:
              
                book = Book(
                    ISBN = col[0],
                    title = col[1],
                    author = col[2],
                    image_url = col[7],
                )

                books.append(book)

                if len(books) > MAX_BOOKS:
                    Book.objects.bulk_create(books)
                    books = []
                    break
                    

            if books:
                Book.objects.bulk_create(books)

    def create_ratings(self):
        MAX_RATINGS = 100
        ratings_path = os.path.abspath("book-review-dataset/BX-Book-Ratings.csv")
        
        with open(ratings_path, "r", encoding='latin-1') as csv_file:
            ratings_data = list(csv.reader(csv_file, delimiter=","))

            ratings = []
            users = list(User.objects.all().values_list('id', flat=True))
            books = list(Book.objects.all().values_list('id', flat=True))


            for col in ratings_data[1:]:
                try:
                    user = User.objects.get(id = col[0])
                except: 
                    rand_id = random.randint(0, len(users)-1)
                    user = User.objects.get(id = users[rand_id])
                    users.pop(rand_id)
                try: 
                    book = Book.objects.get(ISBN = col[1])
                except: 
                    rand_id = random.randint(0, len(books)-1)
                    book = Book.objects.get(id = books[rand_id])
                    books.pop(rand_id)

                REVIEW_PROBABILITY = 0.6
                if random.random() < REVIEW_PROBABILITY:
                    review = 'Good'
                else:
                    review = 'Bad'

                try: 
                    rating = Rating(
                        user = user, 
                        book = book, 
                        rating = col[2],
                        review = review,
                    )

                except: 
                    continue

                ratings.append(rating)

                if len(ratings) > MAX_RATINGS:
                    Rating.objects.bulk_create(ratings)
                    ratings = []
                    break

            if ratings:
                Rating.objects.bulk_create(ratings)




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


    def populate_clubs(self):
        clubs = Club.objects.all()
        user_ids = list(self.users.values_list('id', flat=True))

        for club in clubs:
            sample = User.objects.order_by('?')[:10]
            club.members.add(*sample)
            print(club.id)

