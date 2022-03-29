from bookclub.forms import BookForm, RatingForm , EditRatingForm, BooksSortForm
from bookclub.helpers import SortHelper
from bookclub.models import User, Book, Rating, Club
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, FormView, ListView, UpdateView
from django.views.generic.edit import FormMixin
from system import settings
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse

class AddBookView(LoginRequiredMixin, FormView):
    """Add a book to the site."""

    form_class = BookForm
    template_name = 'add_book.html'

    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.book = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('book_details', kwargs = {'book_id': self.book.id})

class BookDetailsView(LoginRequiredMixin, DetailView, FormMixin):
    """Show individual book details."""

    model = Book
    template_name = 'book_details.html'
    context_object_name = 'book'
    form_class = RatingForm
    pk_url_kwarg = 'book_id'

    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        book = self.get_object()
        rating = book.ratings.all().filter(user=user)
        if rating:
            rating = rating[0]

        context['book'] = book
        context['form'] = RatingForm()
        context['rating'] = rating
        context['reviews'] = book.ratings.all().exclude(review='').exclude(user=user)
        context['reviews_count'] = book.ratings.all().exclude(review='').exclude(user=user).count()
        context['reader'] = book.is_reader(user)
        context['numberOfRatings'] = book.ratings.all().count()
        return context

class BookListView(LoginRequiredMixin, ListView):
    """Show a list of books in book list / club / user."""

    model = Book
    template_name = 'books.html'
    form_class = BooksSortForm()
    paginate_by = settings.BOOKS_PER_PAGE

    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Retrieves the club_id and user_id from url and stores them in self for later use."""
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
    """View to Add a book review."""

    template_name = 'book_details.html'
    pk_url_kwarg = 'book_id'
    form_class = RatingForm

    def get(self, *args, **kwargs):
        """Retrieves the book_id from url and stores it in self for later use."""
        self.book_id = kwargs.get('book_id')
        return super().get(self, *args, **kwargs)

    def form_valid(self, form):
        self.reviewed_book = get_object_or_404(Book.objects, id=self.kwargs['book_id'])
        self.review_user = self.request.user
        if self.reviewed_book.ratings.all().filter(user=self.review_user).exists():
            return HttpResponseForbidden()

        form.instance.user = self.review_user
        form.instance.book = self.reviewed_book
        form.save(self.review_user, self.reviewed_book)
        self.review_user.add_book_to_all_books(self.reviewed_book)

        messages.add_message(self.request, messages.SUCCESS, 'you successfully submitted the review.')

        self.reviewed_book.calculate_average_rating()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                         "Review cannot be over 250 characters.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('book_details', kwargs = {'book_id': self.kwargs['book_id']})

class EditReviewView(LoginRequiredMixin, UpdateView):
    """View to edit the user's review."""

    model = Rating
    template_name = 'edit_review.html'
    pk_url_kwarg = 'review_id'
    form_class = EditRatingForm

    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

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
        return context

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.SUCCESS, "Successfully updated your review!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                         "Review cannot be over 250 characters.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('book_details', kwargs = {'book_id': self.get_object().book.id})