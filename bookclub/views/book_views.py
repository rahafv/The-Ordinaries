from bookclub.forms import BookForm, RatingForm , EditRatingForm, BooksSortForm
from bookclub.helpers import NotificationHelper, SortHelper, get_recommender_books, rec_helper
from bookclub.models import User, Book, Rating, Club
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, FormView, ListView, UpdateView
from django.views.generic.edit import FormMixin
from system import settings
from django.urls import reverse_lazy, reverse
from notifications.signals import notify

class AddBookView(LoginRequiredMixin, FormView):
    form_class = BookForm
    template_name = 'add_book.html'

    def form_valid(self, form):
        self.book = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, "Book added succesfully!")
        return reverse_lazy('book_details', kwargs = {'book_id': self.book.id})


class BookDetailsView(DetailView, FormMixin):
    """Show individual book details."""

    model = Book
    template_name = 'book_details.html'
    context_object_name = 'book'
    form_class = RatingForm
    pk_url_kwarg = 'book_id'

    def get_context_data(self, *args, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        book = self.get_object()
        reviews_count = book.ratings.all().exclude(review='').count()


        if user.is_authenticated:
            reviews = book.ratings.all().exclude(review='').exclude(user=user)
            rating = book.ratings.all().filter(user=user)
            reviews_count = book.ratings.all().exclude(review='').exclude(user=user).count()
            recs = get_recommender_books(self.request, False, 6, user_id=self.request.user.id, book_id=book.id)
        else:
            reviews = book.ratings.all()
            rating = []
            reviews_count = book.ratings.all().exclude(review='').count()
            recs = []

        if rating:
            rating = rating[0]

        context['book'] = book
        context['form'] = RatingForm()
        context['rating'] = rating
        context['reviews'] = reviews
        context['reviews_count'] = reviews_count
        context['reader'] = book.is_reader(user)
        context['numberOfRatings'] = book.ratings.all().count()
        context['recs'] = recs
        return context

class BookListView(ListView):
    model = Book
    template_name = 'books.html'
    form_class = BooksSortForm()
    paginate_by = settings.BOOKS_PER_PAGE


    def get(self, request, *args, **kwargs):
        """Retrieves the club_id from url and stores it in self for later use."""
        self.club_id = kwargs.get('club_id')
        self.user_id = kwargs.get('user_id')
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
        sort = ""
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

class AddReviewView(LoginRequiredMixin, FormView):
    template_name = 'book_details.html'
    pk_url_kwarg = 'book_id'
    form_class = RatingForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['book'] = get_object_or_404(Book.objects, id=self.kwargs['book_id'])
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Book.objects, id=self.kwargs['book_id'])
        return context

    def form_valid(self, form):
        self.reviewed_book = get_object_or_404(Book.objects, id=self.kwargs['book_id'])
        self.review_user = self.request.user
        if self.reviewed_book.ratings.all().filter(user=self.review_user).exists():
            return HttpResponseForbidden()

        form.save()
        self.review_user.add_book_to_all_books(self.reviewed_book)
        rec_helper.increment_counter()
        notify.send(self.review_user, recipient=self.review_user.followers.all(), verb=NotificationHelper().NotificationMessages.REVIEW, action_object=self.reviewed_book, description='user-event-B' )
        messages.add_message(self.request, messages.SUCCESS, 'You successfully submitted the review.')

        self.reviewed_book.calculate_average_rating()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                         "Review cannot be over 250 characters.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('book_details', kwargs = {'book_id': self.kwargs['book_id']})

class EditReviewView(LoginRequiredMixin, UpdateView):
    """View to edit the user's review."""

    model = Rating
    template_name = 'edit_review.html'
    pk_url_kwarg = 'review_id'
    form_class = EditRatingForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['review'] = self.get_object()
        return kwargs

    def get(self, request, *args, **kwargs):
        """Retrieves the review_id from url and stores it in self for later use."""
        self.review_id = kwargs.get('review_id')
        self.review = get_object_or_404(Rating.objects, id=self.review_id)
        if self.request.user != self.review.user:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['review_id'] = self.get_object().id
        context['review'] = self.get_object()
        return context

    def form_valid(self, form):
        form.save()
        rec_helper.increment_counter()
        messages.add_message(self.request, messages.SUCCESS, "Successfully updated your review!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                         "Review cannot be over 250 characters.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('book_details', kwargs = {'book_id': self.get_object().book.id})
