from bookclub.forms import BooksSortForm, ClubsSortForm, UsersSortForm
from bookclub.helpers import get_list_of_objects, getGenres, NotificationHelper, SortHelper
from bookclub.models import User, Book
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic import DetailView
from notifications.signals import notify
from system import settings

class HomeView(LoginRequiredMixin, TemplateView):

    template_name = 'home.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        current_user = self.request.user
        context['user'] = current_user
        notifications = current_user.notifications.unread()
        user_events = notifications.filter(description__contains ='user-event')[:25]
        club_events = notifications.filter(description__contains='club-event')[:10]

        already_selected_books = current_user.books.all()
        my_books = Book.objects.all().exclude(id__in=already_selected_books)
        context['club_events'] = list(club_events)
        context['club_events_length'] = len(club_events)
        context['user_events'] = list(user_events)
        context['books'] = my_books.order_by('-average_rating','-readers_count')[:3]
        return context

class ProfilePageView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'profile_page.html'
    pk_url_kwarg = "user_id"

    def get(self, *args, **kwargs):
        """Retrieves the user_id and is_clubs from url and stores it in self for later use."""
        self.user_id = kwargs.get('user_id', None)
        self.is_clubs = kwargs.get('is_clubs', False)
        if self.user_id == self.request.user.id:
            return redirect('profile')
        return super().get(self.request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User.objects, id=self.request.user.id)

        if self.user_id:
            user = get_object_or_404(User.objects, id=self.user_id)

        if self.user_id is not None:
            books_queryset = User.objects.get(id=self.user_id).books.all()
            books_count = books_queryset.count()
            books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
            page_number = self.request.GET.get('page')
            books = books_pg.get_page(page_number)
            context['items'] = books
            context['items_count'] = books_count

        context['current_user'] = self.request.user
        context['user'] = user
        context['following'] = self.request.user.is_following(user)
        context['followable'] = (self.request.user != user)

        return context

@login_required
def add_book_to_list(request, book_id):
    book = get_object_or_404(Book.objects, id=book_id)
    user = request.user
    if book.is_reader(user):
        book.remove_reader(user)
        messages.add_message(request, messages.SUCCESS, "Book Removed!")
    else:
        book.add_reader(user)
        request.user.add_book_to_all_books(book)
        notificationHelper = NotificationHelper()
        notificationHelper.delete_notifications(user, user.followers.all(), notificationHelper.NotificationMessages.ADD, book )
        notify.send(user, recipient=user.followers.all(), verb=notificationHelper.NotificationMessages.ADD, action_object=book, description='user-event-B' )
        messages.add_message(request, messages.SUCCESS, "Book Added!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))


class SearchPageView(LoginRequiredMixin, TemplateView):

    template_name = 'search_page.html'
    paginate_by = settings.MEMBERS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        searched = self.request.GET.get('searched')
        category = self.request.GET.get('category')

        label = category

        # method in helpers to return a dictionary with a list of users, clubs or books searched
        search_page_results = get_list_of_objects(
            searched=searched, label=label)
        category = search_page_results["category"]
        filtered_list = search_page_results["filtered_list"]

        sortForm = ""
        if(category == "Clubs"):
            sortForm = ClubsSortForm(self.request.GET or None)
        elif(category == "Books"):
            sortForm = BooksSortForm(self.request.GET or None)
        else:
            sortForm = UsersSortForm(self.request.GET or None)

        if (sortForm.is_valid()):
            sort = sortForm.cleaned_data.get('sort')
            sort_helper = SortHelper(sort, filtered_list)

            if(category == "Clubs"):
                filtered_list = sort_helper.sort_clubs()
            elif(category == "Books"):
                filtered_list = sort_helper.sort_books()
            else:
                filtered_list = sort_helper.sort_users()

        context['searched'] = searched
        context['category'] = category
        context['label'] = label
        pg = Paginator(filtered_list, settings.MEMBERS_PER_PAGE)
        page_number = self.request.GET.get('page')
        filtered_list = pg.get_page(page_number)
        context['filtered_list'] = filtered_list
        context['form'] = sortForm
        context['current_user'] = self.request.user
        return context

class InitialBookListView(LoginRequiredMixin, TemplateView):
    template_name = 'initial_book_list.html'

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

class InitialGenresView(LoginRequiredMixin, TemplateView):
    template_name = 'initial_genres.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genres = getGenres()
        context['genres'] = sorted(genres, reverse=True, key=genres.get)[0:40]
        return context

@login_required
def add_book_to_list(request, book_id):
    book = get_object_or_404(Book.objects, id=book_id)
    user = request.user
    if book.is_reader(user):
        book.remove_reader(user)
        messages.add_message(request, messages.SUCCESS, "Book Removed!")
    else:
        book.add_reader(user)
        request.user.add_book_to_all_books(book)
        notificationHelper = NotificationHelper()
        notificationHelper.delete_notifications(user, user.followers.all(), notificationHelper.NotificationMessages.ADD, book )
        notify.send(user, recipient=user.followers.all(), verb=notificationHelper.NotificationMessages.ADD, action_object=book, description='user-event-B' )
        messages.add_message(request, messages.SUCCESS, "Book Added!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))