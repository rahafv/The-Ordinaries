from bookclub.helpers import create_event, SortHelper
from bookclub.models import User, Book, Event
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from system import settings

@login_required
def home(request):
    def events_created_at(event):
        return event.created_at

    current_user = request.user
    authors = list(current_user.followees.all()) + [current_user]
    clubs = list(User.objects.get(id=current_user.id).clubs.all())
    user_events = []
    club_events = []
    for author in authors:
        user_events += list(Event.objects.filter(user=author))
    final_user_events = user_events
    final_user_events.sort(reverse=True, key=events_created_at)
    first_twentyFive = final_user_events[0:25]

    for club in clubs:
        club_events += list(Event.objects.filter(club=club))

    final_club_events = club_events
    final_club_events.sort(reverse=True, key=events_created_at)
    first_ten = final_club_events[0:10]

    club_events_length = len(first_ten)

    already_selected_books = current_user.books.all()
    my_books = Book.objects.all().exclude(id__in=already_selected_books)
    top_rated_books = my_books.order_by('-average_rating','-readers_count')[:3]

    return render(request, 'home.html', {'user': current_user, 'user_events': first_twentyFive, 'club_events': first_ten, 'club_events_length': club_events_length, 'books':top_rated_books})

@login_required
def show_profile_page(request, user_id=None, is_clubs=False):
    user = get_object_or_404(User.objects, id=request.user.id)

    if user_id == request.user.id:
        return redirect('profile')

    if user_id:
        user = get_object_or_404(User.objects, id=user_id)
        

    following = request.user.is_following(user)
    followable = (request.user != user)

    items = ""
    items_count = 0

    if user_id is not None:
        books_queryset = User.objects.get(id=user_id).books.all()
        books_count = books_queryset.count()
        books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
        page_number = request.GET.get('page')
        books = books_pg.get_page(page_number)
        items = books
        items_count = books_count

        return render(request, 'profile_page.html', {'current_user': request.user, 'user': user, 'following': following, 'followable': followable, 'items': items, 'items_count': items_count, 'is_clubs': is_clubs})
       
    return render(request, 'profile_page.html', {'current_user': request.user, 'user': user, 'following': following, 'followable': followable, })

@login_required
def add_book_to_list(request, book_id):
    book = get_object_or_404(Book.objects, id=book_id)
    user = request.user
    if book.is_reader(user):
        book.remove_reader(user)
        messages.add_message(request, messages.SUCCESS, "Book Removed!")
    else:
        book.add_reader(user)
        create_event('U', 'B', Event.EventType.ADD, user=user, book=book)
        messages.add_message(request, messages.SUCCESS, "Book Added!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))

@login_required
def search_page(request):
    if request.method == 'GET':
        searched = request.GET.get('searched')
        category = request.GET.get('category')
        label = category

        # method in helpers to return a dictionary with a list of users, clubs or books searched
        search_page_results = get_list_of_objects(
            searched=searched, label=label)
        category = search_page_results["category"]
        filtered_list = search_page_results["filtered_list"]

        sortForm = ""
        if(category == "Clubs"):
            sortForm = NameAndDateSortForm(request.GET or None)
        else:
            sortForm = NameSortForm(request.GET or None)

        pg = Paginator(filtered_list, settings.MEMBERS_PER_PAGE)
        page_number = request.GET.get('page')
        filtered_list = pg.get_page(page_number)
        current_user=request.user
        return render(request, 'search_page.html', {'searched': searched, 'category': category, 'label': label, "filtered_list": filtered_list, "form": sortForm, "current_user":current_user})

    else:
        return render(request, 'search_page.html', {})

#wait for rahaf's ver
@login_required
def initial_book_list(request):
    current_user = request.user
    already_selected_books = current_user.books.all()
    my_books = Book.objects.all().exclude(id__in=already_selected_books)
    list_length = len(current_user.books.all())
    sorted_books = my_books.order_by('-average_rating','-readers_count')[:8]
    return render(request, 'initial_book_list.html', {'my_books':sorted_books , 'user':current_user , 'list_length':list_length })

