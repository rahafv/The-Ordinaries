import random
from faker import Faker
import os
from bookclub.models import User, Book
import csv

class Excel():
    def __init__(self):
        self.faker = Faker('en_US')
        print("test")


    def create_users(self):

        header = ['username', 'ISBN', 'rating']

        data = []

        self.users = User.objects.all()
        self.user_ids = list(self.users.values_list('id', flat=True))
        
        books = Book.objects.all()
        book_ids = list(books.values_list('id', flat=True))

        pairs = []
        ctr = 0 

        while ctr < 100000: 
            user_id = random.randint(0, self.users.count()-1)
            book_id = random.randint(0, books.count()-1)
            
            if (user_id, book_id) not in pairs:

                user = User.objects.get(id=self.user_ids[user_id]).username
                book= Book.objects.get(id=book_ids[book_id]).ISBN
                Rating = random.randint(0,10)

                data.append([user, book, Rating])

                pairs.append((user_id,book_id))
                ctr+=1

            else:
                print("pass")
                pass


        with open(r"/Users/Rahaf/Desktop/The-Ordinaries/book-review-dataset/ratings.csv", 'w+', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            writer.writerow(header)
            writer.writerows(data)

