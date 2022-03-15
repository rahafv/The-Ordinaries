from bookclub.forms import BookForm, RatingForm , EditRatingForm, NameSortForm
from bookclub.helpers import create_event, get_list_of_objects, SortHelper
from bookclub.models import User, Book, Event, Rating, Club
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from system import settings

@login_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            return redirect('book_details', book_id=book.id)
    else:
        form = BookForm()
    return render(request, "add_book.html", {"form": form})

@login_required
def book_details(request, book_id):
    book = get_object_or_404(Book.objects, id=book_id)
    numberOfRatings=book.ratings.all().count()
    form = RatingForm()
    user = request.user
    check_reader = book.is_reader(user)
    reviews = book.ratings.all().exclude(review="").exclude(user=request.user)
    rating = book.ratings.all().filter(user=request.user)
    if rating:
        rating = rating[0]
    reviews_count = book.ratings.all().exclude(
        review="").exclude(user=request.user).count()
    context = {'book': book, 'form': form,
               'rating': rating, 'reviews': reviews,
               'reviews_count': reviews_count, 'user': user, 'reader': check_reader, 'numberOfRatings':numberOfRatings}
    return render(request, "book_details.html", context)

@login_required
def add_review(request, book_id):
    reviewed_book = get_object_or_404(Book.objects, id=book_id)
    review_user = request.user
    if reviewed_book.ratings.all().filter(user=review_user).exists():
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            form.instance.user = review_user
            form.instance.book = reviewed_book
            form.save(review_user, reviewed_book)
            create_event('U', 'B', Event.EventType.REVIEW, user=review_user, book=reviewed_book)
            messages.add_message(request, messages.SUCCESS, "you successfully submitted the review.")

            reviewed_book.calculate_average_rating() 

            return redirect('book_details', book_id=reviewed_book.id)

    messages.add_message(request, messages.ERROR,
                         "Review cannot be over 250 characters.")
    return render(request, 'book_details.html', {'book': reviewed_book})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Rating.objects, id=review_id)
    review_user = request.user
    if review_user == review.user:
        if request.method == "POST":
            form = EditRatingForm(data = request.POST, instance=review)
            if form.is_valid():
                form.save(review_user, review.book)
                messages.add_message(request, messages.SUCCESS, "Successfully updated your review!")
                return redirect('book_details', book_id= review.book.id)
            messages.add_message(request, messages.ERROR, "Review cannot be over 250 characters!")
        else:
            form = EditRatingForm(instance = review)
        
        return render(request, 'edit_review.html', {'form':form , 'review_id':review.id })

    else:
        return render(request, '404_page.html', status=404)


@login_required
def books_list(request, club_id=None, user_id=None):
    books_queryset = Book.objects.all()
    general = True
    if club_id:
        books_queryset = Club.objects.get(id=club_id).books.all()
        general = False
    if user_id:
        books_queryset = User.objects.get(id=user_id).books.all()
        general = False

    form = NameSortForm(request.GET or None)
    sort = ""

    if form.is_valid():
        sort = form.cleaned_data.get('sort')
        sort_helper = SortHelper(sort, books_queryset)
        books_queryset = sort_helper.sort_books()

    count = books_queryset.count()
    books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
    page_number = request.GET.get('page')
    books = books_pg.get_page(page_number)
    return render(request, 'books.html', {'books': books, 'general': general, 'count': count, 'form': form})
