from bookclub.forms import NameSortForm, NameAndDateSortForm
from bookclub.helpers import create_event, get_list_of_objects, SortHelper
from bookclub.models import User, Book, Event
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic import DetailView
from system import settings

class HomeView(TemplateView):

    template_name = 'home.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def events_created_at(self, event):
        return event.created_at

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        current_user = self.request.user

        authors = list(current_user.followees.all()) + [current_user]
        clubs = list(User.objects.get(id=current_user.id).clubs.all())
        user_events = []
        club_events = []
        for author in authors:
            user_events += list(Event.objects.filter(user=author))

        final_user_events = user_events
        final_user_events.sort(reverse=True, key=self.events_created_at)
        context['user_events'] = final_user_events[0:25]

        for club in clubs:
            club_events += list(Event.objects.filter(club=club))

        final_club_events = club_events
        final_club_events.sort(reverse=True, key=self.events_created_at)
        first_ten = final_club_events[0:10]
        context['club_events'] = first_ten
        context['club_events_length'] = len(first_ten)

        already_selected_books = current_user.books.all()
        my_books = Book.objects.all().exclude(id__in=already_selected_books)
        context['books'] = my_books.order_by('-average_rating','-readers_count')[:3]

        context['user'] = current_user
        return context

# @login_required
# def home(request):
#     def events_created_at(event):
#         return event.created_at

#     current_user = request.user
#     authors = list(current_user.followees.all()) + [current_user]
#     clubs = list(User.objects.get(id=current_user.id).clubs.all())
#     user_events = []
#     club_events = []
#     for author in authors:
#         user_events += list(Event.objects.filter(user=author))
#     final_user_events = user_events
#     final_user_events.sort(reverse=True, key=events_created_at)
#     first_twentyFive = final_user_events[0:25]

#     for club in clubs:
#         club_events += list(Event.objects.filter(club=club))

#     final_club_events = club_events
#     final_club_events.sort(reverse=True, key=events_created_at)
#     first_ten = final_club_events[0:10]

#     club_events_length = len(first_ten)

#     already_selected_books = current_user.books.all()
#     my_books = Book.objects.all().exclude(id__in=already_selected_books)
#     top_rated_books = my_books.order_by('-average_rating','-readers_count')[:3]

#     return render(request, 'home.html', {'user': current_user, 'user_events': first_twentyFive, 'club_events': first_ten, 'club_events_length': club_events_length, 'books':top_rated_books})


class ProfilePageView(DetailView):
    model = User
    pk_url_kwarg = 'review_id'
    # paginate_by = settings.BOOKS_PER_PAGE

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Retrieves the user_id from url and stores it in self for later use."""
        self.user_id = kwargs.get('user_id')
        self.is_clubs = kwargs.get('is_clubs')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.user_id:
            user = get_object_or_404(User.objects, id=self.user_id)
        else:
            user = get_object_or_404(User.objects, id=request.user.id)

        if self.user_id == request.user.id:
            return redirect('profile')

        context['current_user'] = request.user
        context['user'] = user
        context['following'] = request.user.is_following(user)
        context['followable'] = (request.user != user)

        if self.user_id:
            books_queryset = User.objects.get(id=self.user_id).books.all()
            books_count = books_queryset.count()
            books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
            page_number = request.GET.get('page')
            books = books_pg.get_page(page_number)
            context['items'] = books
            context['items_count'] = books_count
        return context


class InitialGenresView(TemplateView):
    template_name = 'initial_genres.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genres = getGenres()
        context['genres'] = sorted(genres, reverse=True, key=genres.get)[0:40]
        return context


# @login_required
# def initial_genres(request):
#     genres = getGenres()
#     sorted_genres = sorted(genres, reverse=True, key=genres.get)[0:40]

#     return render(request, 'initial_genres.html', {'genres':sorted_genres})

class InitialBookListView(TemplateView):
    template_name = 'initial_book_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        already_selected_books = current_user.books.all()
        my_books = Book.objects.all().exclude(id__in=already_selected_books)

        genres = self.request.GET.getlist('genre')
        if genres:
            for genre in genres:
                my_books = my_books.filter(genre__contains=genre)

        sorted_books = my_books.order_by('-average_rating','-readers_count')[:8]

        context['my_books'] = sorted_books
        context['list_length'] = len(current_user.books.all())
        context['genres'] = genres
        return context


# @login_required
# def initial_book_list(request):
#     current_user = request.user
#     already_selected_books = current_user.books.all()
#     my_books = Book.objects.all().exclude(id__in=already_selected_books)

#     genres = request.GET.getlist('genre')
#     if genres:
#         for genre in genres:
#             my_books = my_books.filter(genre__contains=genre)

#     sorted_books = my_books.order_by('-average_rating','-readers_count')[:8]

#     list_length = len(current_user.books.all())
#     return render(request, 'initial_book_list.html', {'my_books':sorted_books , 'list_length':list_length, 'genres':genres})
