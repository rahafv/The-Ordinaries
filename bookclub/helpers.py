from django.shortcuts import redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.conf import settings
from .models import Event, User, Club, Book
from django.db.models.functions import Lower


def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

def create_event(type_of_actor, type_of_action, message, user=None, club=None, meeting=None, book=None, rating=None, action_user=None):
    event = Event(
                type_of_actor = type_of_actor,
                type_of_action = type_of_action,
                message = message,
                user = user ,
                club = club,
                meeting = meeting,
                book = book, 
                rating = rating,
                action_user = action_user
            )

    event.save()
    return event

def delete_event(type_of_actor, type_of_action, message, user=None, club=None, meeting=None, book=None, rating=None, action_user=None):
    event = Event.objects.filter(type_of_actor = type_of_actor, type_of_action = type_of_action, message = message, user = user , club = club, meeting = meeting, book = book, rating = rating, action_user = action_user)
    event.delete()

class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.email_verified))


    
generate_token = TokenGenerator()


def sort_users(sort_value, list_of_users):
    if(sort_value == 'name_desc'):
            return list_of_users.reverse()
    else:
        return list_of_users

def sort_books(sort, list_of_books):
    if(sort == 'name_asc'):
        return list_of_books.order_by(Lower('title').asc())
    elif (sort == 'name_desc'):
        return list_of_books.order_by(Lower('title').desc())
    elif(sort == "date_asc"):
        return list_of_books.order_by('year')
    else:
        return list_of_books.order_by(Lower('year').desc())

def sort_clubs(sort, list_of_clubs):
    if(sort == 'name_asc'):
        return list_of_clubs.order_by(Lower('name').asc())
    elif (sort == 'name_desc'):
        return list_of_clubs.order_by(Lower('name').desc())
    elif(sort == "date_asc"):
        return list_of_clubs.order_by('created_at')
    else:
        return list_of_clubs.order_by('-created_at')

 
def get_list_of_objects(searched, label):

    category = ''
    filtered_list = ""

    if(label=="user-name"):
        filtered_list = User.objects.filter(username__contains=searched)
        category= "Users"
    elif(label=="user-location"):
        filtered_list = User.objects.filter(country__contains=searched)
        category= "Users"
    elif(label=="club-name"):
        filtered_list = Club.objects.filter(name__contains=searched)
        category= "Clubs"
    elif(label=="club-location"):
        filtered_list = Club.objects.filter(country__contains=searched)
        category= "Clubs"
    elif(label=="book-title"):
        filtered_list = Book.objects.filter(title__contains=searched)
        category= "Books"
    elif(label=="book-year"):
        filtered_list = Book.objects.filter(year__contains=searched)
        category= "Books"
    else:
        filtered_list = Book.objects.filter(author__contains=searched)
        category= "Books"
    
    return {
        "category" : category, 
        "filtered_list" : filtered_list}

