from django.shortcuts import redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.conf import settings
from .models import Event

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
