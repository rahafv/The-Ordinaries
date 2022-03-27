from django.core.management.base import BaseCommand
from bookclub.models import User, Club, Book , Rating, Meeting
from faker import Faker
import csv
import time
import os
from .unseed import unseed
import random
from datetime import datetime, timedelta
import pytz
from notifications.signals import notify
from bookclub.helpers import NotificationHelper


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
        count = int((self.users.count()-1)/10)
        for club in self.clubs:
            rand_num = random.randint(0, count)
            sample = User.objects.order_by('?')[:rand_num]
            club.members.add(*sample)

            club.members.add(club.owner)
            notify.send(club.owner, recipient=club.owner.followers.all(), verb=self.notificationHelper.NotificationMessages.CREATE, action_object=club, description='user-event-C' ) 
            
            self.create_meeting(club, club.owner)
            

    def create_meeting(self, club, chooser):
        meeting = Meeting.objects.create(
            title = 'Meeting 1',
            club = club,
            chooser = chooser,
            book = Book.objects.first(),
            time = pytz.utc.localize(datetime.today()+timedelta(15)),
            link = 'https://us04web.zoom.us/j/74028123722?pwd=af96piEWRe9_XWlB1XnAjw4XDp4uk7.1'

        )
        notify.send(club, recipient=club.members.all(), verb=self.notificationHelper.NotificationMessages.SCHEDULE, action_object=meeting, description='club-event-M' )      

    def create_books(self):
        MAX_BOOKS = 1000
        books_path = os.path.abspath("book-review-dataset/books.csv")
        with open(books_path, "r", encoding='latin-1') as csv_file:
            books_data = csv.reader(csv_file, delimiter=",")
            next(books_data)

            books = []

            for col in books_data:
              
                image_url = self.check_blank_image(col[3])

                book = Book(
                    ISBN = col[4],
                    title = col[6],
                    author = col[0],
                    genre = col[7],
                    description = col[1],
                    image_url = image_url,
                    pages_num = col[5]
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
  
        books = Book.objects.all()
        book_ids = list(books.values_list('id', flat=True))

        pairs = []
        ratings = []

        for col in range(MAX_RATINGS):
            user_id = random.randint(0, self.users.count()-1)
            book_id = random.randint(0, books.count()-1)

            user = self.users.get(id = self.user_ids[user_id])
            book = books.get(id = book_ids[book_id])

            REVIEW_PROBABILITY = 0.6
            if random.random() < REVIEW_PROBABILITY:
                review = 'it was fine'
            else:
                review = 'the book was okay'

            rating = random.randint(0,10)

            pair = (user, book)

            if not pair in pairs: 

                rating = Rating(
                    user = user, 
                    book = book, 
                    rating = rating,
                    review = review,
                )

                book.add_reader(user)
                user.add_book_to_all_books(book)

                rand = random.randint(0,1)
                if rand == 1:
                    notify.send(user, recipient=user.followers.all(), verb=self.notificationHelper.NotificationMessages.ADD, action_object=book, description='user-event-B' )
                else:
                    notify.send(user, recipient=user.followers.all(), verb=self.notificationHelper.NotificationMessages.REVIEW, action_object=book, description='user-event-B' )       

                pairs.append(pair)
                ratings.append(rating)

            else: 
                continue

        Rating.objects.bulk_create(ratings)


    def calculate_average(self):
        ratings=Rating.objects.all()
        for rating in ratings:
            rating.save()

    def check_blank_image(self, image_url):
        if image_url == '':
            return 'https://i.imgur.com/f6LoJwT.jpg'
        return image_url