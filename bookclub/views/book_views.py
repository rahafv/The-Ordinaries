from bookclub.forms import BookForm, RatingForm , EditRatingForm, BooksSortForm
from bookclub.helpers import NotificationHelper, SortHelper, get_recommender_books, rec_helper
from bookclub.models import User, Book, Rating, Club
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, FormView, ListView, UpdateView
from django.views.generic.edit import FormMixin
from system import settings
from django.urls import reverse_lazy, reverse
from notifications.signals import notify
from django.contrib.auth.decorators import login_required

class AddBookView(LoginRequiredMixin, FormView):
    """Handle add book."""
    form_class = BookForm
    template_name = 'book_templates/add_book.html'

    def form_valid(self, form):
        """Save book after form is validated."""
        self.book = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        messages.add_message(
            self.request, messages.SUCCESS, "Book added succesfully!")
        return reverse_lazy('book_details', kwargs = {'book_id': self.book.id})


class BookDetailsView(DetailView, FormMixin):
    """Show individual book details."""

    model = Book
    template_name = 'book_templates/book_details.html'
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
            recs = get_recommender_books(self.request, False, 6, user_id=user.id, book_id=book.id)
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
    """Show book lst."""
    model = Book
    template_name = 'book_templates/books.html'
    form_class = BooksSortForm()
    paginate_by = settings.BOOKS_PER_PAGE


    def get(self, request, *args, **kwargs):
        """Retrieves the club_id from url and stores it in self for later use."""
        self.club_id = kwargs.get('club_id')
        self.user_id = kwargs.get('user_id')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Generate context data to be shown in the template."""
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
    """Add review to a book."""
    template_name = 'book_templates/book_details.html'
    pk_url_kwarg = 'book_id'
    form_class = RatingForm

    def get_form_kwargs(self):
        """Generate data that the form needs to initialise."""
        kwargs = super().get_form_kwargs()
        kwargs['book'] = get_object_or_404(Book.objects, id=self.kwargs['book_id'])
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Book.objects, id=self.kwargs['book_id'])
        return context

    def form_valid(self, form):
        """Process valid form."""
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
        """Process invalid form"""
        messages.add_message(self.request, messages.ERROR,
                         "Review cannot be over 250 characters.")
        return super().form_invalid(form)

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        return reverse('book_details', kwargs = {'book_id': self.kwargs['book_id']})

class EditReviewView(LoginRequiredMixin, UpdateView):
    """Edit the user's review."""

    model = Rating
    template_name = 'book_templates/edit_review.html'
    pk_url_kwarg = 'review_id'
    form_class = EditRatingForm

    def get_form_kwargs(self):
        """Generate data that the form needs to initialise."""
        kwargs = super().get_form_kwargs()
        kwargs['review'] = self.get_object()
        return kwargs

    def get(self, request, *args, **kwargs):
        """Retrieve the review_id from url and store it in self for later use."""
        self.review_id = kwargs.get('review_id')
        self.review = get_object_or_404(Rating.objects, id=self.review_id)
        if self.request.user != self.review.user:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['review_id'] = self.get_object().id
        context['review'] = self.get_object()
        return context

    def form_valid(self, form):
        """Process valid form."""
        form.save()
        rec_helper.increment_counter()
        messages.add_message(self.request, messages.SUCCESS, "Successfully updated your review!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Process invalid form."""
        messages.add_message(self.request, messages.ERROR,
                         "Review cannot be over 250 characters.")
        return super().form_invalid(form)

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        return reverse('book_details', kwargs = {'book_id': self.get_object().book.id})

"""Post user's progress of reading a book."""
@login_required
def post_book_progress(request, book_id):
    book = get_object_or_404(Book.objects, id=book_id)
    user = request.user
    if request.method == "POST":
        progress = request.POST.get('progress')
        if progress != '':
            comment = request.POST.get("comment")
            fullcomment=""
            if comment:
                fullcomment = f" commented:   \"{comment}\" for "
            else:
                fullcomment = " has read"
            label = request.POST.get('label')
            notify.send(user, recipient=[user] + list(user.followers.all()), verb=(f' {fullcomment} {progress} {label} of '), action_object=book, description='user-event-B' )
            messages.add_message(request, messages.SUCCESS,"Successfully updated progress!")
        else:
            messages.add_message(request, messages.ERROR,"Progress cannot be updated with invalid value!")
    return redirect('book_details', book_id=book.id)

