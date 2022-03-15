from bookclub.models import User, Book, Event
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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