from bookclub.forms import BookForm, RatingForm , EditRatingForm, NameSortForm, BooksSortForm
from bookclub.helpers import create_event, get_list_of_objects, SortHelper
from bookclub.models import User, Book, Event, Rating, Club
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, FormView, ListView, UpdateView
from django.views.generic.edit import FormMixin
from system import settings
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

class AddBookView(FormView):
    form_class = BookForm
    template_name = 'add_book.html' 
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.book = form.save()
        return super().form_valid(form)

    def get_success_url(self):         
        return reverse_lazy('book_details', kwargs = {'book_id': self.book.id})

# @login_required
# def add_book(request):
#     if request.method == "POST":
#         form = BookForm(request.POST)
#         if form.is_valid():
#             book = form.save()
#             return redirect('book_details', book_id=book.id)
#     else:
#         form = BookForm()
#     return render(request, "add_book.html", {"form": form})

class BookDetailsView(DetailView, FormMixin):
    model = Book
    template_name = 'book_details.html'
    context_object_name = 'book'
    form_class = RatingForm
    pk_url_kwarg = 'book_id'
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        book = self.get_object()
        rating = book.ratings.all().filter(user=user)
        if rating:
            rating = rating[0]
        
        context['book'] = book
        context['rating'] = rating
        context['form'] = RatingForm()
        context['reviews'] = book.ratings.all().exclude(review='').exclude(user=user)
        context['reviews_count'] = book.ratings.all().exclude(review='').exclude(user=user).count()
        context['reader'] = book.is_reader(user)
        context['numberOfRatings'] = book.ratings.all().count()
        return context

# @login_required
# def book_details(request, book_id):
#     book = get_object_or_404(Book.objects, id=book_id)
#     numberOfRatings=book.ratings.all().count()
#     form = RatingForm()
#     user = request.user
#     check_reader = book.is_reader(user)
#     reviews = book.ratings.all().exclude(review='').exclude(user=request.user)
    
#     if rating:
#         rating = rating[0]
#     reviews_count = book.ratings.all().exclude(review='').exclude(user=request.user).count()
#     context = {'book': book, 'form': form,
#                'rating': rating, 'reviews': reviews,
#                'reviews_count': reviews_count, 'user': user, 'reader': check_reader, 'numberOfRatings':numberOfRatings}
#     return render(request, "book_details.html", context)

class AddReviewView(FormView):
    form_class = RatingForm
    template_name = 'book_details.html' 
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.reviewed_book = get_object_or_404(Book.objects, id=self.kwargs['book_id'])
        self.review_user = self.request.user

        form.instance.user = self.review_user
        form.instance.book = self.reviewed_book
        form.save(self.review_user, self.reviewed_book)

        create_event('U', 'B', Event.EventType.REVIEW, user=self.review_user, book=self.reviewed_book)
        messages.add_message(self.request, messages.SUCCESS, 'you successfully submitted the review.')
        
        self.reviewed_book.calculate_average_rating() 
        return super().form_valid(form)

    def get_success_url(self):         
        # if self.reviewed_book.ratings.all().filter(user=self.review_user).exists():
            # return HttpResponseForbidden()
        # else:
        return reverse_lazy('book_details', kwargs = {'book_id': self.reviewed_book.id})

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

class EditReviewView(FormView):
    model = Rating
    template_name = 'edit_review.html' 
    pk_url_kwarg = 'review_id'
    form_class = EditRatingForm


    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    # def get(self, request, *args, **kwargs):
    #     """Retrieves the club_id from url and stores it in self for later use."""
    #     self.review_id = kwargs.get('review_id')  
    #     return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        review_user = self.request.user
        review = get_object_or_404(Rating.objects, id=self.review_id)
        if review_user != review.user:
            raise Http404

        form.save(review_user, review.book)
        messages.add_message(self.request, messages.SUCCESS, "Successfully updated your review!")

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                         "Review cannot be over 250 characters.")
        return super().form_invalid(form)

    def get_success_url(self): 
        return reverse_lazy('book_details', kwargs = {'book_id': self.review.book.id})
    


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


class BookListView(ListView):
    model = Book
    template_name = 'books.html'
    form_class = BooksSortForm
    paginate_by = settings.BOOKS_PER_PAGE

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Retrieves the club_id from url and stores it in self for later use."""
        self.club_id = kwargs.get('club_id') 
        self.user_id = kwargs.get('club_id') 
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        books_queryset = Book.objects.all()
        general = True
        if self.club_id:
            books_queryset = Club.objects.get(id=self.club_id).books.all()
            general = False
        if self.user_id:
            books_queryset = User.objects.get(id=self.user_id).books.all()
            general = False
        form = BooksSortForm(self.request.GET or None)
        if form.is_valid():
            sort = form.cleaned_data.get('sort')
            sort_helper = SortHelper(sort, books_queryset)
            books_queryset = sort_helper.sort_books()

        books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
        page_number = self.request.GET.get('page')
        books = books_pg.get_page(page_number)
        context['books'] = books
        context['general'] = general
        context['form'] = form
        context['count'] = books_queryset.count()
        return context


# @login_required
# def books_list(request, club_id=None, user_id=None):
#     books_queryset = Book.objects.all()
#     general = True
#     if club_id:
#         books_queryset = Club.objects.get(id=club_id).books.all()
#         general = False
#     if user_id:
#         books_queryset = User.objects.get(id=user_id).books.all()
#         general = False

#     form = NameSortForm(request.GET or None)
#     sort = ""

#     if form.is_valid():
#         sort = form.cleaned_data.get('sort')
#         sort_helper = SortHelper(sort, books_queryset)
#         books_queryset = sort_helper.sort_books()

#     count = books_queryset.count()
#     books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
#     page_number = request.GET.get('page')
#     books = books_pg.get_page(page_number)
#     return render(request, 'books.html', {'books': books, 'general': general, 'count': count, 'form': form})
