from faker import Faker
import os
import csv
class Excel():
    def __init__(self):
        self.faker = Faker('en_US')
        print("test")


    def create_users(self):

        header = ['name', 'theme', 'city', 'country']

        data = []
        
        for i in range(1, 10000): 
            name = self.faker.word()
            theme= self.faker.sentence(nb_words=4)
            city = self.faker.city()
            country = self.faker.country()
            data.append([name, theme, city, country])


        with open(r"C:\Users\talaa\VSCode\The-Ordinaries\book-review-dataset\Clubs.csv", 'w+', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            writer.writerow(header)
            writer.writerows(data)

ex = Excel()
ex.create_users()
print("test")
