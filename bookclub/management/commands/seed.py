import csv
import os
import random
import time
from datetime import datetime, timedelta

import pytz
from bookclub.helpers import NotificationHelper
from bookclub.models import Book, Club, Meeting, Rating, User
from django.core.management.base import BaseCommand
from faker import Faker
from notifications.signals import notify

from .unseed import unseed


class Command(BaseCommand):

    DEFAULT_PASSWORD = 'pbkdf2_sha256$260000$4BNvFuAWoTT1XVU8D6hCay$KqDCG+bHl8TwYcvA60SGhOMluAheVOnF1PMz0wClilc='

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        self.notificationHelper = NotificationHelper()

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
        self.create_books()
        end = time.time()
        print("book: ", end - start)

        start = time.time()
        self.create_clubs()
        self.clubs = Club.objects.all()
        self.populate_clubs()
        end = time.time()
        print("club: ", end - start)

        start = time.time()
        self.create_ratings()
        end = time.time()
        print("ratings: ", end - start)

        self.calculate_average()
        
        print("total time: ", end - initial_start)

    def create_users(self):

        MAX_USERS = 150
        users_path = os.path.abspath("book-review-dataset/Users.csv")
        with open(users_path, "r", encoding='latin-1') as csv_file:
            users_data = csv.reader(csv_file, delimiter=",")
            next(users_data)

            users = []
    
            for row in users_data:

                if row[2].isdigit():
                    age = int(row[2])
                else:
                    age = None

                user = User(
                    first_name = row[0],
                    last_name = row[1],
                    username = row[5],
                    email = row[5]+"@example.org",
                    age = age,
                    city = self.get_city(row[6]),
                    region = self.get_region(row[6]),
                    country = self.get_country(row[6]),
                    bio = row[4],
                    password = Command.DEFAULT_PASSWORD,
                    email_verified = True,
                    # training_counter = 0
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
        count = int((self.users.count())/25)
        for user in self.users:
            rand_num = random.randint(0, count)
            sample = User.objects.order_by('?').exclude(id=user.id)[:rand_num]
            user.followers.add(*sample)


    def create_clubs(self):
        MAX_CLUBS = 24
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
                    name = col[0] + " club",
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
        count = int((self.users.count())/25)
        books = Book.objects.order_by('?')
        MEETING_PROBABILITY = 0.5
        ctr = 0

        for club in self.clubs:
            rand_num = random.randint(1, count)
            sample = User.objects.order_by('?')[:rand_num]
            club.members.add(*sample)

            club.members.add(club.owner)
            notify.send(club.owner, recipient=club.owner.followers.all(), verb=self.notificationHelper.NotificationMessages.CREATE, action_object=club, description='user-event-C' ) 
            
            if random.random() < MEETING_PROBABILITY:
                self.create_meeting(club, club.owner, books[ctr])
            ctr +=1
            
        
    def create_meeting(self, club, chooser, book):
        meeting = Meeting.objects.create(
            title = 'Meeting 1',
            club = club,
            chooser = chooser,
            book = book,
            time = pytz.utc.localize(datetime.today()+timedelta(15)),
            link = 'https://us04web.zoom.us/j/74028123722?pwd=af96piEWRe9_XWlB1XnAjw4XDp4uk7.1'
        )
        book.add_club(club)
        notify.send(club, recipient=club.members.all(), verb=self.notificationHelper.NotificationMessages.SCHEDULE, action_object=meeting, description='club-event-M')

    def create_books(self):
        MAX_BOOKS = 500
        books_path = os.path.abspath("book-review-dataset/books.csv")
        with open(books_path, "r", encoding='latin-1') as csv_file:
            books_data = csv.reader(csv_file, delimiter=",")
            next(books_data)

            books = []

            for col in books_data:
              
                image_url = self.check_blank_image(col[2])

                book = Book(
                    ISBN = col[3],
                    title = col[5],
                    author = col[0],
                    genre = col[6],
                    description = col[1],
                    image_url = image_url,
                    pages_num = col[4]
                )

                books.append(book)

                if len(books) > MAX_BOOKS:
                    Book.objects.bulk_create(books)
                    books = []
                    break
                    
            if books:
                Book.objects.bulk_create(books)
                

    def create_ratings(self):
        MAX_RATINGS = 2000

        ratings_path = os.path.abspath("book-review-dataset/ratings.csv")
        with open(ratings_path, "r", encoding='latin-1') as csv_file:
            ratings_data = csv.reader(csv_file, delimiter=",")
            next(ratings_data)

            ratings = []
  
            for col in ratings_data:

                REVIEW_PROBABILITY = 0.6
                if random.random() < REVIEW_PROBABILITY:
                    review = 'it was fine'
                else:
                    review = 'the book was okay'

                try:
                    user = User.objects.get(username=col[0])
                    book = Book.objects.get(ISBN=col[1])
                except:
                    continue
                

                rating = Rating(
                    user = user, 
                    book = book, 
                    rating = col[2],
                    review = review,
                )

                book.add_reader(user)
                user.add_book_to_all_books(book)

                if random.random() < REVIEW_PROBABILITY:
                    rand = random.randint(0,2)
                    if rand == 0:
                        notify.send(user, recipient=user.followers.all(), verb=self.notificationHelper.NotificationMessages.ADD, action_object=book, description='user-event-B' )
                    elif rand == 1:
                        notify.send(user, recipient=user.followers.all(), verb=self.notificationHelper.NotificationMessages.REVIEW, action_object=book, description='user-event-B' )       
                    else:
                        pass
           
                ratings.append(rating)

                if len(ratings) > MAX_RATINGS:
                    Rating.objects.bulk_create(ratings)
                    ratings = []
                    break

            if ratings:
                Rating.objects.bulk_create(ratings)

    def calculate_average(self):
        ratings=Rating.objects.all()
        for rating in ratings:
            rating.save()

    def check_blank_image(self, image_url):
        if image_url == '':
            return 'https://i.imgur.com/f6LoJwT.jpg'
        return image_url
