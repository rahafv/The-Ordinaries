from faker import Faker
import os
import csv
class Excel():
    def __init__(self):
        self.faker = Faker('en_GB')
        print("test")


    def create_users(self):
        # users_path = r"C:\Users\talaa\VSCode\The-Ordinaries\book-review-dataset\BX_Users.csv"
        # with open(users_path, "r", encoding='latin-1') as csv_file:
        #     users_data = list(csv.reader(csv_file, delimiter=";"))

        header = ['first_name', 'last_name', 'username', 'email', 'bio']

        data = []
        
        for i in range(1, 278860): 
            first_name= self.faker.first_name()
            last_name= self.faker.last_name()
            username = self.create_username(first_name, last_name)
            data.append([first_name, last_name, username, "", self.faker.text(max_nb_chars=300)])

        # user2_path = r"C:\Users\talaa\VSCode\The-Ordinaries\book-review-dataset\Users.csv"

        with open(r"C:\Users\talaa\VSCode\The-Ordinaries\book-review-dataset\Users.csv", 'w+', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            writer.writerow(header)
            writer.writerows(data)


    def create_username(self, first_name, last_name):
        return first_name.lower() + last_name.lower()

    def create_email(self, username):
        return username + "@example.org"

ex = Excel()
ex.create_users()
print("test")
