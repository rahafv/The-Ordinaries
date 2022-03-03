from django.core.management.base import BaseCommand
from bookclub.models import User, Club, Book , Rating
from faker import Faker
import csv
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
        self.user_ids = list(self.users.values_list('id', flat=True))

        self.create_followers()
        end = time.time()
        print("users: ", end - start)

        start = time.time()
        self.create_clubs()
        self.populate_clubs()
        end = time.time()
        print("club: ", end - start)

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

        MAX_USERS = 500
        users_path = os.path.abspath("book-review-dataset/Users.csv")
        with open(users_path, "r", encoding='latin-1') as csv_file:
            users_data = csv.reader(csv_file, delimiter=",")
            next(users_data)

            users = []
    
            for row in users_data:

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

    def create_followers(self):
        count = int((self.users.count()-1)/10)
        for user in self.users:
            rand_num = random.randint(0, count)
            sample = User.objects.order_by('?').exclude(id=user.id)[:rand_num]
            user.followers.add(*sample)


    def create_clubs(self):
        MAX_CLUBS = 100
        clubs_path = os.path.abspath("book-review-dataset/Clubs.csv")
        with open(clubs_path, "r", encoding='latin-1') as csv_file:
            clubs_data = csv.reader(csv_file, delimiter=",")
            next(clubs_data)

            clubs = []
            for col in clubs_data:
                rand_id = random.randint(0, self.users.count()-1)

                TYPE_PROBABILITY = 0.1
                if random.random() < TYPE_PROBABILITY:
                    club_type = 'Private'
                else:
                    club_type = 'Public'
                
                club = Club(
                    name = col[4] + " club",
                    owner = User.objects.get(id = self.user_ids[rand_id]),
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

    def populate_clubs(self):
        clubs = Club.objects.all()
        count = int((self.users.count()-1)/10)
        for club in clubs:
            rand_num = random.randint(0, count)
            sample = User.objects.order_by('?')[:rand_num]
            club.members.add(club.owner)
            club.members.add(*sample)


    def create_books(self):
        MAX_BOOKS = 1000
        books_path = os.path.abspath("book-review-dataset/BX_Books.csv")
        with open(books_path, "r", encoding='latin-1') as csv_file:
            books_data = csv.reader(csv_file, delimiter=",")
            next(books_data)

            books = []

            for col in books_data:
              
                book = Book(
                    ISBN = col[0],
                    title = col[1],
                    author = col[2],
                    image_url = col[7],
                    year= col[3]
                )

                books.append(book)

                if len(books) > MAX_BOOKS:
                    Book.objects.bulk_create(books)
                    books = []
                    break
                    
            if books:
                Book.objects.bulk_create(books)
                

    def create_ratings(self):
        MAX_RATINGS = 1000
        ratings_path = os.path.abspath("book-review-dataset/BX-Book-Ratings.csv")
       
        with open(ratings_path, "r", encoding='latin-1') as csv_file:
            ratings_data = csv.reader(csv_file, delimiter=",")
            next(ratings_data)

            books = Book.objects.all()
            book_ids = list(books.values_list('id', flat=True))

            pairs = []
            ratings = []

            for col in ratings_data:
                user_id = random.randint(0, self.users.count()-1)
                book_id = random.randint(0, books.count()-1)

                user = self.users.get(id = self.user_ids[user_id])
                book = books.get(id = book_ids[book_id])

                REVIEW_PROBABILITY = 0.6
                if random.random() < REVIEW_PROBABILITY:
                    review = 'it was fine'
                else:
                    review = 'the book was okay'

                pair = (user, book)

                if not pair in pairs: 

                    rating = Rating(
                        user = user, 
                        book = book, 
                        rating = col[2],
                        review = review,
                    )

                    pairs.append(pair)
                    ratings.append(rating)

                else: 
                    continue

                if len(ratings) > MAX_RATINGS:
                    Rating.objects.bulk_create(ratings)
                    ratings = []
                    break

            if ratings:
                Rating.objects.bulk_create(ratings)
