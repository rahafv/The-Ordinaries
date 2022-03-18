from collections import defaultdict
from functools import reduce
import math
from django.shortcuts import redirect
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail 
import six
from django.conf import settings
from .models import Event, Rating, User, Club, Book
from django.db.models.functions import Lower
from bookclub.recommender.rec import Recommender
from collections import ChainMap, Counter

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

class MeetingHelper:
    def assign_rand_book(self, meeting, book, request=None):
        if not meeting.book and request:
            meeting.assign_book(book)
            self.send_email(request=request, 
                meeting=meeting, 
                subject='A book has be chosen', 
                letter='emails/book_confirmation.html', 
                all_mem=True
            )

    def get_email(self, meeting, all_mem):
        if all_mem:
            invitees = meeting.club.members.values_list('email', flat=True)
            return invitees

        else:
            return [meeting.chooser.email]

    def send_email(self, request, meeting, subject, letter, all_mem):
        current_site = get_current_site(request)
        subject = subject
        body = render_to_string(letter, {
            'domain': current_site,
            'meeting': meeting,
        })
        send_mail(subject, body, settings.EMAIL_HOST_USER, self.get_email(meeting, all_mem))

class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.email_verified))
    
generate_token = TokenGenerator()

class SortHelper:

    def __init__(self, sort_value, list_of_filtered_objects):
        self.sort = sort_value
        self.list_of_objects = list_of_filtered_objects

    def sort_users(self):
        if(self.sort == 'name_desc'):
            return self.list_of_objects.reverse()
        else:
            return self.list_of_objects

    def sort_books(self):
        if(self.sort == 'name_asc'):
            return self.list_of_objects.order_by(Lower('title').asc())
        elif (self.sort == 'name_desc'):
            return self.list_of_objects.order_by(Lower('title').desc())
        elif (self.sort == 'rating_asc'):
            return self.list_of_objects.order_by('average_rating')
        else :
            return self.list_of_objects.order_by('-average_rating')

    def sort_clubs(self):
        if(self.sort == 'name_asc'):
            return self.list_of_objects.order_by(Lower('name').asc())
        elif (self.sort == 'name_desc'):
            return self.list_of_objects.order_by(Lower('name').desc())
        elif(self.sort == "date_asc"):
            return self.list_of_objects.order_by('created_at')
        else:
            return self.list_of_objects.order_by('-created_at')

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
    elif(label=="book-genre"):
        filtered_list = Book.objects.filter(genre__contains=searched)
        category= "Books"
    else:
        filtered_list = Book.objects.filter(author__contains=searched)
        category= "Books"
    
    return {
        "category" : category, 
        "filtered_list" : filtered_list}

class RecommendationHelper:
    def get_recommendations(self, num_of_rec, user_id, book_id=None):
        recommendations = []
        if not book_id:
            if Rating.objects.filter(user_id=user_id):
                recommender = Recommender()
                recommendations = recommender.get_recommendations(user_id, num_of_rec)
                
            else:
                recommendations = self.get_genre_recommendations(user_id)[:num_of_rec]
        
        else:
            recommendations = list(self.get_book_recommendations(user_id, book_id).keys())[:num_of_rec]
            
        return self.get_books(recommendations)

    def get_book_recommendations(self, user_id, book_id):
        book = Book.objects.get(id=book_id)
        user = User.objects.get(id=user_id)
        books = user.books.all()
        all_books = Book.objects.all().exclude(id__in=books).exclude(id=book.id)

        genres = self.getGenres()
        similarity = {}    
        for b in all_books:
            num = self.computeGenreSimilarity(book.id, b.id, genres)
            if num > 0:
                similarity[b.id] = num

        sorted_similarity = dict(sorted(similarity.items(), reverse=True, key=lambda item: item[1]))
        return sorted_similarity

    def get_genre_recommendations(self, user_id):
        user = User.objects.get(id=user_id)
        books = user.books.all()

        similarity = []   
        for book in books:
            sim = self.get_book_recommendations(user_id, book.id)
            similarity.append(sim)
        
        similarity = ChainMap(*similarity)
        sorted_similarity = sorted(similarity, reverse=True, key=similarity.get)
        return sorted_similarity

    def computeGenreSimilarity(self, book1, book2, genres):
        genres1 = genres[book1]
        genres2 = genres[book2]
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(genres1)):
            x = genres1[i]
            y = genres2[i]
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        
        if sumxx*sumyy == 0:
            return 0

        return sumxy/math.sqrt(sumxx*sumyy)

    def getGenres(self):
        genres = defaultdict(list)
        genreIDs = {}
        maxGenreID = 0
        books = Book.objects.all()
        
        for book in books:
            book_id = book.id
            genreList = book.genre.split(',')
            genreIDList = []
            
            for genre in genreList:
                if genre in genreIDs:
                    genreID = genreIDs[genre]
                else:
                    genreID = maxGenreID
                    genreIDs[genre] = genreID
                    maxGenreID += 1
                genreIDList.append(genreID)
            
            genres[book_id] = genreIDList
        
        # Convert integer-encoded genre lists to bitfields that we can treat as vectors
        for (book_id, genreIDList) in genres.items():
            bitfield = [0] * maxGenreID
            for genreID in genreIDList:
                bitfield[genreID] = 1
            genres[book_id] = bitfield            
        
        return genres

    def get_books(self, recommendations):
        books = []
        for rec_id in recommendations:
            books.append(Book.objects.get(id=rec_id))
        
        return books

    def get_club_recommendations(self, num_of_rec, club_id):
        club = Club.objects.get(id=club_id)
        members = club.members.order_by("?") #Fix later
        books = club.books.all() #remove from recommendations

        recommendations =  []
        for mem in members:
            recommendations.append(self.get_recommendations(num_of_rec, mem.id))

        all_recommendations = reduce(lambda z, y :z + y, recommendations)
        counter = Counter(all_recommendations)
        counter_list = counter.most_common(num_of_rec)
        final_recommendations = [ seq[0] for seq in counter_list ]
        return final_recommendations

