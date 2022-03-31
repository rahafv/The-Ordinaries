from datetime import timedelta
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from .forms import SignUpForm, LogInForm, CreateClubForm, PasswordForm, UserForm, RatingForm , EditRatingForm, MeetingForm, BooksSortForm, UsersSortForm, ClubsSortForm, TransferOwnershipForm, BookForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .helpers import get_list_of_objects, generate_token, MeetingHelper, SortHelper, NotificationHelper, getGenres, get_recommender_books, rec_helper
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat, Meeting, User, Club, Book , Rating
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, FormView
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from system import settings
from threading import Timer
from django.core.paginator import Paginator
from notifications.signals import notify
from notifications.utils import slug2id
from notifications.models import Notification
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import  DetailView, SingleObjectMixin
from django.views.generic.base import TemplateView
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, FormView, ListView, UpdateView
from django.views.generic.edit import FormMixin, CreateView
from django.utils.decorators import method_decorator
import humanize
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views.generic import ListView


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to direct to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url'"
            )
        else:
            return self.redirect_when_logged_in_url


class HomeView(TemplateView):

    template_name = 'home.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        current_user = self.request.user
        context['user'] = current_user
        
        if current_user.is_authenticated:
            notifications = current_user.notifications.unread()
            user_events = notifications.filter(description__contains ='user-event')[:25]
            club_events = notifications.filter(description__contains='club-event')[:10]
            top_rated_books = get_recommender_books(self.request, True, 3, user_id=current_user.id)
        else:
            notifications = None
            user_events = []
            club_events = []
            books = Book.objects.all()
            top_rated_books = books.order_by('-average_rating','-readers_count')[:3]

        context['club_events'] = list(club_events)
        context['club_events_length'] = len(club_events)
        context['user_events'] = list(user_events)
        context['books'] = top_rated_books
        return context


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


class SignUpView(LoginProhibitedMixin, FormView):
    """Handles user sign up."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN
    user = None

    def form_valid(self, form):
        """Saves the user when form is validated."""
        self.user = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        return reverse('send_verification', kwargs={'user_id':self.user.id})



def send_activiation_email(request, user_id):

    user = get_object_or_404(User, id=user_id)

    if not user.email_verified:
        current_site = get_current_site(request)
        subject = 'Activate your account'
        body = render_to_string('emails/activate.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)}
        )
        email_from = settings.EMAIL_HOST_USER
        email_to = [user.email]

        send_mail(subject, body, email_from, email_to)

        messages.add_message(request, messages.WARNING,
                             'Your email needs verification!')
    else:
        messages.add_message(request, messages.WARNING,
                             'Email is already verified!')

    return redirect('log_in')

class ActivateUserView(TemplateView):
    """Handles activation of a user after their email is verified."""

    template_name = "activate-fail.html"

    def get(self, *args, **kwargs):
        """Retrieves user if valid and sets its email verified field to true."""
        try:
            uid = force_text(urlsafe_base64_decode(kwargs["uidb64"]))
            self.user = User.objects.get(pk=uid)
        except:
            self.user = None

        if self.user and generate_token.check_token(self.user, kwargs["token"]):
            self.user.email_verified = True
            self.user.save()
            messages.add_message(self.request, messages.SUCCESS, 'Account verified!')
            return redirect(reverse('log_in'))

        return super().get(*args, **kwargs)


    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template"""
        context = super().get_context_data(**kwargs)
        context["user"] = self.user
        return context



class LogInView(LoginProhibitedMixin, FormView):
    """Handle log in attempt."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'home'

    def get(self, request):
        """Display log in template."""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or ''
        user = form.get_user()

        if user and not user.email_verified:
            messages.add_message(request, messages.ERROR,
                "Email is not verified, please check your email inbox!")
            return render(request, 'log_in.html', {'form': form, 'next': self.next, 'request': request, 'user': user})

        if user:
            login(request, user)
            if len(user.books.all()) == 0:
                redirect_url = self.next or 'initial_genres'
            else:
                redirect_url = self.next or 'home'
            return redirect(redirect_url)

        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def handler404(request, exception):
    return render(exception, '404_page.html', status=404)

"""Handle log out attempt."""
@login_required
def log_out(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "You've been logged out!")
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""
        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""
        messages.add_message(self.request, messages.SUCCESS, 'Password updated!')
        return reverse('home')

class CreateClubView(LoginRequiredMixin, CreateView):
    """Handle creation of new club."""

    model = Club
    template_name = 'create_club.html'
    form_class = CreateClubForm

    def form_valid(self, form):
        """Process a valid form."""
        club_owner = self.request.user
        form.instance.owner = club_owner
        self.club = form.save()
        notify.send(club_owner, recipient=club_owner.followers.all(), verb=NotificationHelper().NotificationMessages.CREATE, action_object=self.club, description='user-event-C' )
        self.club.add_member(club_owner)
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        return reverse('club_page', kwargs={"club_id": self.club.id})

    def handle_no_permission(self):
        """If there is no permission, redirect to log in."""
        return redirect(reverse('log_in') + '?next=/create_club/')

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


class ClubPageView(LoginRequiredMixin, DetailView):
    """Show individual club details."""

    model = Club
    template_name = 'club_page.html'
    pk_url_kwarg = 'club_id'
    context_object_name = 'club'

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data()
        user = self.request.user

        context['is_member'] = context['club'].is_member(user)
        context['is_applicant'] = context['club'].is_applicant(user)
        upcoming_meetings = context['club'].get_upcoming_meetings()
        try:
            context['upcoming_meeting'] = upcoming_meetings[0]
        except:
            context['upcoming_meeting']=None

        return context

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

class AddBookView(LoginRequiredMixin, FormView):
    form_class = BookForm
    template_name = 'add_book.html'

    def form_valid(self, form):
        self.book = form.save()
        rec_helper.increment_counter()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('book_details', kwargs = {'book_id': self.book.id})


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

# @login_required
# def show_profile_page(request, user_id=None, is_clubs=False):
#     user = get_object_or_404(User.objects, id=request.user.id)

#     if user_id == request.user.id:
#         return redirect('profile')

#     if user_id:
#         user = get_object_or_404(User.objects, id=user_id)


#     following = request.user.is_following(user)
#     followable = (request.user != user)

#     items = ""
#     items_count = 0

#     if user_id is not None:
#         books_queryset = User.objects.get(id=user_id).books.all()
#         books_count = books_queryset.count()
#         books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
#         page_number = request.GET.get('page')
#         books = books_pg.get_page(page_number)
#         items = books
#         items_count = books_count

#         return render(request, 'profile_page.html', {'current_user': request.user, 'user': user, 'following': following, 'followable': followable, 'items': items, 'items_count': items_count, 'is_clubs': is_clubs})

#     return render(request, 'profile_page.html', {'current_user': request.user, 'user': user, 'following': following, 'followable': followable, })


class ProfilePageClubsView(LoginRequiredMixin, ListView):
    model = Club
    template_name = 'profile_page.html'
    pk_url_kwarg = "user_id"

    def get(self, *args, **kwargs):
        """Retrieves the user_id and is_clubs from url and stores it in self for later use."""
        self.user_id = kwargs.get('user_id', None)
        return super().get(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User.objects, id=self.user_id)

        context['following'] = self.request.user.is_following(user)
        context['followable'] = (self.request.user != user)

        clubs_queryset = user.clubs.all()
        context['items_count'] = clubs_queryset.count()
        clubs_pg = Paginator(clubs_queryset, settings.CLUBS_PER_PAGE)
        page_number = self.request.GET.get('page')
        context['items'] = clubs_pg.get_page(page_number)

        context['current_user'] = self.request.user
        context['user'] = user
        context['is_clubs'] = True

        return context


"""View to add link to clubs_list in user profile """
# @login_required
# def show_profile_page_clubs(request, user_id=None):
#     user = get_object_or_404(User.objects, id=request.user.id)

#     user = get_object_or_404(User.objects, id=user_id)

#     following = request.user.is_following(user)
#     followable = (request.user != user)

#     # clubs_queryset = get_list_or_404(Club, owner = user )
#     clubs_queryset = user.clubs.all()
#     clubs_count = clubs_queryset.count()
#     clubs_pg = Paginator(clubs_queryset, settings.CLUBS_PER_PAGE)
#     page_number = request.GET.get('page')
#     clubs = clubs_pg.get_page(page_number)

#     return render(request, 'profile_page.html', {'current_user': request.user, 'user': user, 'following': following, 'followable': followable, 'items': clubs, 'items_count': clubs_count, 'is_clubs': True})

class ProfilePageReadingListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'profile_page.html'
    pk_url_kwarg = "user_id"

    def get(self, *args, **kwargs):
        """Retrieves the user_id and is_clubs from url and stores it in self for later use."""
        self.user_id = kwargs.get('user_id', None)
        return super().get(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User.objects, id=self.user_id)

        context['following'] = self.request.user.is_following(user)
        context['followable'] = (self.request.user != user)

        books_queryset = user.books.all()
        context['items_count'] = books_queryset.count()
        books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
        page_number = self.request.GET.get('page')
        context['items'] = books_pg.get_page(page_number)

        context['current_user'] = self.request.user
        context['user'] = user
        context['is_clubs'] = False

        return context

""" View to add link to reading_list tto user profile """
# @login_required
# def show_profile_page_reading_list(request, user_id):
#     user = get_object_or_404(User.objects, id=request.user.id)

#     user = get_object_or_404(User.objects, id=user_id)

#     following = request.user.is_following(user)
#     followable = (request.user != user)

#     books_queryset = user.books.all()
#     books_count = books_queryset.count()
#     books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
#     page_number = request.GET.get('page')
#     books = books_pg.get_page(page_number)

#     return render(request, 'profile_page.html', {'current_user': request.user, 'user': user, 'following': following, 'followable': followable, 'items': books, 'items_count': books_count, 'is_clubs': False})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = UserForm
    template_name = "edit_profile.html"
    form_class = UserForm

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to update the date_of_birth of the given user"""
        kwargs = super(ProfileUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(
            self.request, messages.SUCCESS, "Profile updated!")
        return reverse('profile')


"""Enable user to join a club."""
@login_required
def join_club(request, club_id):

    club = get_object_or_404(Club.objects, id=club_id)
    user = request.user
    notificationHelper = NotificationHelper()

    if club.is_member(user):
        messages.add_message(request, messages.ERROR,
                             "Already a member of this club!")
        return redirect('club_page', club_id)

    if club.club_type == "Private":
        if not club.is_applicant(user):
            club.applicants.add(user)
            notify.send(user, recipient=club.owner, verb=notificationHelper.NotificationMessages.APPLIED, action_object=club,  description='notification' )
            messages.add_message(request, messages.SUCCESS,
                                 "You have successfully applied!")
            return redirect('club_page', club_id)
        else:
            messages.add_message(request, messages.ERROR,
                                 "Already applied, awaiting approval!")
            return redirect('club_page', club_id)

    club.members.add(user)
    notificationHelper.delete_notifications(user, user.followers.all(), notificationHelper.NotificationMessages.JOIN, club )
    notify.send(user, recipient=user.followers.all(), verb=notificationHelper.NotificationMessages.JOIN, action_object=club, description='user-event-C' )

    messages.add_message(request, messages.SUCCESS, "Joined club!")
    return redirect('club_page', club_id)


"""Enable a user to withdraw from a club."""
@login_required
def withdraw_club(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    user = request.user

    if user == club.owner:
        messages.add_message(request, messages.ERROR,
                             "Ownership must be transferred before withdrawing from club!")
        return redirect('club_page', club_id)

    if not club.is_member(user):
        messages.add_message(request, messages.ERROR,
                             "You are not a member of this club!")
        return redirect('club_page', club_id)

    club.members.remove(user)
    notificationHelper = NotificationHelper()
    notificationHelper.delete_notifications(user, user.followers.all(), notificationHelper.NotificationMessages.WITHDRAW, club )
    notify.send(user, recipient=user.followers.all(), verb=notificationHelper.NotificationMessages.WITHDRAW, action_object=club, description='user-event-C' )

    messages.add_message(request, messages.SUCCESS, "Withdrew from club!")
    return redirect('club_page', club_id)

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

class ClubsListView(ListView):
    """Display list of clubs."""

    model = Club
    template_name = "clubs.html"
    paginate_by = settings.CLUBS_PER_PAGE


    def get(self, request, *args, **kwargs):
        """Retrieves the user_id from url (if exists) and stores it in self for later use."""
        self.user_id = kwargs.get("user_id")
        self.privacy = self.request.GET.get('privacy')
        self.ownership = self.request.GET.get('ownership')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """If user_id is provided return all clubs the user is a member in, else return all clubs."""
        self.general = True
        self.clubs_queryset = super().get_queryset()
        self.user = self.request.user

        if self.user_id:
            self.user = User.objects.get(id=self.user_id)
            self.clubs_queryset = self.user.clubs.all()
            self.general = False

        self.form = ClubsSortForm(self.request.GET or None)

        if self.form.is_valid():
            sort = self.form.cleaned_data.get('sort')
            sort_helper = SortHelper(sort, self.clubs_queryset)
            self.clubs_queryset = sort_helper.sort_clubs()

        self.filtered = False
        if self.privacy == 'public':
            self.clubs_queryset = self.clubs_queryset.filter(club_type='Public')
            self.filtered = True
        elif self.privacy == 'private':
            self.clubs_queryset = self.clubs_queryset.filter(club_type='Private')
            self.filtered = True

        if self.ownership == 'owned':
            self.clubs_queryset = self.clubs_queryset.filter(owner=self.user)
            self.filtered = True

        return self.clubs_queryset

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""

        context = super().get_context_data(**kwargs)
        context['general'] = self.general
        context['privacy'] = self.privacy
        context['ownership'] = self.ownership
        context['filtered'] = self.filtered
        context['form'] = self.form
        context['clubs'] = context["page_obj"]
        context['count'] = self.object_list.count()

        return context

class MembersListView(LoginRequiredMixin, ListView):
    """Display list of members."""

    model = User
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieves the club_id from url and stores it in self for later use."""
        self.club_id = kwargs.get("club_id")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Return all members of a club if the user has access, else return an empty queryset."""
        self.club = get_object_or_404(Club, id=self.club_id)
        self.form = UsersSortForm(self.request.GET or None)
        if(self.club.is_member(self.request.user)):
            self.members_queryset = self.club.members.all()
            if self.form.is_valid():
                sort = self.form.cleaned_data.get('sort')
                sort_helper = SortHelper(sort, self.members_queryset)
                self.members_queryset = sort_helper.sort_users()

            return self.members_queryset
        return self.model.objects.none()

    def get_template_names(self):
        """Returns a different template name if the user does not have access rights."""
        if self.club.is_member(self.request.user):
            return ['members_list.html']
        else:
            messages.add_message(self.request, messages.ERROR, "You cannot access the members list!" )
            return ['club_page.html']

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['members'] = context["page_obj"]
        context['club'] = self.club
        context['current_user'] = self.request.user
        context['form'] = self.form
        return context


class FollowingListView(LoginRequiredMixin, ListView):
    """Display following list of a user."""

    model = User
    template_name = "follow_list.html"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieves the user_id from url and stores it in self for later use."""
        self.user_id = kwargs.get("user_id")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Returns following list of a user."""
        self.user = get_object_or_404(User, id=self.user_id)
        return self.user.followees.all()

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['follow_list'] = context["page_obj"]
        context['user'] =self.user
        context['is_following'] = True
        context['current_user'] = self.request.user
        return context


class FollowersListView(LoginRequiredMixin, ListView):
    """Displays followers list of a user."""

    model = User
    template_name = "follow_list.html"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieves the user_id from url and stores it in self for later use."""
        self.user_id = kwargs.get("user_id")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Returns followers list of a user."""
        self.user = get_object_or_404(User, id=self.user_id)
        return self.user.followers.all()

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['follow_list'] = context["page_obj"]
        context['user'] = self.user
        context['is_following'] = False
        context['current_user'] = self.request.user
        return context


class ApplicantsListView(LoginRequiredMixin, ListView):
    """Displays applicants list of a club."""

    model = User
    template_name = "applicants_list.html"
    context_object_name = "applicants"

    def get(self, request, *args, **kwargs):
        """Retrieves the club_id from url and stores it in self for later use."""
        self.club_id = kwargs.get("club_id")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Return all applicants of a club if the user is owner, else return an empty queryset."""
        self.club = get_object_or_404(Club, id=self.club_id)
        self.form = UsersSortForm(self.request.GET or None)
        if(self.club.owner == self.request.user):
            self.applicants_queryset = self.club.applicants.all()
            if self.form.is_valid():
                sort = self.form.cleaned_data.get('sort')
                sort_helper = SortHelper(sort, self.applicants_queryset)
                self.applicants_queryset = sort_helper.sort_users()

            return self.applicants_queryset
        return self.model.objects.none()

    def get_template_names(self):
        """Returns a different template name if the user is not owner."""
        if self.club.owner == self.request.user:
            return ['applicants_list.html']
        else:
            messages.add_message(self.request, messages.ERROR, "You cannot access the applicants list!" )
            return ['club_page.html']

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['is_owner'] = self.club.owner == self.request.user
        context['club'] = self.club
        context['current_user'] = self.request.user
        context['form'] = self.form
        return context

@login_required
def accept_applicant(request, club_id, user_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    applicant = get_object_or_404(User.objects, id=user_id)
    if(current_user == club.owner):
        club.members.add(applicant)
        club.applicants.remove(applicant)
        notify.send(applicant, recipient=applicant.followers.all(), verb=NotificationHelper().NotificationMessages.JOIN, action_object=club, description='user-event-C' )
        messages.add_message(request, messages.SUCCESS, "Applicant accepted!")
        notify.send(current_user, recipient=applicant, verb= NotificationHelper().NotificationMessages.ACCEPT, action_object=club, description='notification' )
        return redirect('applicants_list', club_id)
    else:
        messages.add_message(request, messages.ERROR,
                             "You cannot change applicant's status!")
        return redirect('club_page', club_id)


@login_required
def reject_applicant(request, club_id, user_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    applicant = get_object_or_404(User.objects, id=user_id)
    if(current_user == club.owner):
        club.applicants.remove(applicant)
        messages.add_message(request, messages.WARNING, "Applicant rejected!")
        notify.send(current_user, recipient=applicant, verb=NotificationHelper().NotificationMessages.REJECT, action_object=club,  description='notification')
        return redirect('applicants_list', club_id)
    else:
        messages.add_message(request, messages.ERROR,
                             "You cannot change applicant's status!")
        return redirect('club_page', club_id)

class TransferClubOwnershipView(LoginRequiredMixin, FormView, SingleObjectMixin):
    """Enables owner to transfer ownership to another member."""

    template_name = "transfer_ownership.html"
    form_class = TransferOwnershipForm
    pk_url_kwarg = "club_id"
    context_object_name = "club"
    model = Club

    def get_form_kwargs(self):
        """Generates data that the form needs to initialise."""
        kwargs = super().get_form_kwargs()
        kwargs["club_id"] = self.get_object().id
        kwargs["user_id"] = self.request.user.id
        return kwargs

    def get_context_data(self, **kwargs):
        """Set self.object to store club."""
        self.object = self.get_object()
        return super().get_context_data(**kwargs)

    def get(self, *args, **kwargs):
        """Get method with additonal checks for permissions."""
        club = self.get_object()
        if self.request.user != club.owner:
            messages.add_message(self.request, messages.ERROR, "You are not permitted to access this page!")
            return redirect('club_page', club_id = club.id)

        members = club.members.all().exclude(id=self.request.user.id)
        if members.count() == 0:
            messages.add_message(self.request, messages.WARNING, "There are no other members to tranfer the club to!")
            return redirect('club_page', club_id = club.id)

        return super().get(*args, **kwargs)

    def form_valid(self, form):
        """Changes the owner after the form is validated."""
        self.club = self.get_object()
        member = form.cleaned_data.get("new_owner")
        self.club.make_owner(member)
        notify.send(self.club, recipient=self.club.members.all(), verb=NotificationHelper().NotificationMessages.TRANSFER, action_object=member, description='club-event-U' )

        current_site = get_current_site(self.request)
        subject = self.club.name + ' Club updates'
        email_from = settings.EMAIL_HOST_USER

        members_email_body = render_to_string('emails/transfer.html', {
        'owner': member,
        'domain': current_site,
        'club':self.club
        })

        owner_email_body = render_to_string('emails/new_owner.html', {
        'owner': member,
        'domain': current_site,
        'club':self.club
        })

        email_to_members = self.club.members.exclude(id=member.id).values_list('email', flat=True)
        email_to_owner = [member.email]

        send_mail(subject, members_email_body, email_from, email_to_members)
        send_mail(subject, owner_email_body, email_from, email_to_owner)

        messages.add_message(self.request, messages.SUCCESS, "Ownership transferred!")
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        return reverse('club_page', kwargs={"club_id": self.club.id})


class EditClubInformationView(LoginRequiredMixin, UpdateView):
    """View that handles club information change requests."""
    model = Club
    fields = ['name', 'theme', 'meeting_type', 'club_type','city','country']
    template_name = "edit_club_info.html"
    pk_url_kwarg = "club_id"

    def get_context_data(self, **kwargs):
        """Set self.object to store club_id."""
        context = super().get_context_data(**kwargs)
        context['club_id'] = self.object.id
        return context

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        messages.add_message(self.request, messages.SUCCESS, "Successfully updated club information!")
        return reverse('club_page', args=[self.object.id])

class ScheduleMeetingView(LoginRequiredMixin, FormView):
    template_name = "schedule_meeting.html"
    form_class = MeetingForm

    def get_context_data(self, **kwargs):
        """Extract club_id from self and store it in the context."""
        context = super().get_context_data(**kwargs)
        context["club_id"] = self.club_id
        return context

    def get_form_kwargs(self):
        """Generates data that the form needs to initialise."""
        kwargs = super().get_form_kwargs()
        kwargs["club"] = get_object_or_404(Club.objects, id=self.club_id)
        return kwargs

    def get(self, *args, **kwargs):
        """Extracts club id and stores it in self for later use."""
        self.club_id = kwargs["club_id"]
        self.club = get_object_or_404(Club.objects, id=self.club_id)
        if self.request.user != self.club.owner:
            raise Http404

        #check that the club has members
        if self.club.members.count() <= 1:
            messages.add_message(self.request, messages.ERROR, "There are no members!")
            return redirect('club_page', club_id=self.club.id)

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Check that user is owner upon form submission."""
        self.club_id = kwargs["club_id"]
        self.club = get_object_or_404(Club.objects, id=self.club_id)

        if self.request.user != self.club.owner:
            raise Http404

        return super().post(*args, **kwargs)

    def form_valid(self, form):
        """Process valid form."""
        meeting = form.save()
        #send email invites
        MeetingHelper().send_email(request=self.request,
            meeting=meeting,
            subject='A New Meeting Has Been Scheduled',
            letter='emails/meeting_invite.html',
            all_mem=True
        )

        if meeting.chooser:
            #send email to member who has to choose a book
            MeetingHelper().send_email(request=self.request,
                meeting=meeting,
                subject='It Is Your Turn!',
                letter='emails/chooser_reminder.html',
                all_mem=False
            )

            rec_book = get_recommender_books(self.request, True, 1, club_id=meeting.club.id)[0]
                        
            deadline = timedelta(7).total_seconds()  # 0.00069444
            Timer(deadline, MeetingHelper().assign_rand_book, [meeting, rec_book, self.request]).start()

        notify.send(self.club, recipient=self.club.members.all(), verb=NotificationHelper().NotificationMessages.SCHEDULE, action_object=meeting, description='club-event-M' )
        messages.add_message(self.request, messages.SUCCESS, "Meeting has been scheduled!")
        return redirect('club_page', club_id=self.club_id)


class ChoiceBookListView(LoginRequiredMixin, TemplateView):
    template_name = "choice_book_list.html"
    model = Book

    def get_context_data(self, *args, **kwargs):
        """Generate context data for the template."""
        context = super().get_context_data(*args, **kwargs)
        meeting = get_object_or_404(Meeting.objects, id=kwargs["meeting_id"])
        if self.request.user == meeting.chooser and not meeting.book:
            read_books = meeting.club.books.all()
            my_books =  Book.objects.all().exclude(id__in = read_books)
            context["rec_books"] = my_books.order_by('-average_rating','-readers_count')[0:24]
            return context
        else:
            raise Http404


class SearchBookView(LoginRequiredMixin, ListView):
    template_name = "choice_book_list.html"
    model = Book
    paginate_by = settings.BOOKS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieves the searched term from the query string and stores it in self for later use."""
        self.searched = self.request.GET.get('searched', '')
        self.meeting_id = kwargs["meeting_id"]
        return super().get(request, *args, **kwargs)


    def get_queryset(self):
        """Returns filtered book list based on the searched term."""
        books = Book.objects.filter(title__contains=self.searched)
        return books

    def get_context_data(self, **kwargs):
        """Generate context data for the template."""
        context = super().get_context_data(**kwargs)
        meeting = get_object_or_404(Meeting.objects, id=self.meeting_id)
        if self.request.user == meeting.chooser and not meeting.book:
            context["searched"] = self.searched
            context["books"] = context["page_obj"]
            context["meeting_id"] = self.meeting_id
            return context
        else:
            raise Http404

"""Allow user to choose a book for a meeting."""
@login_required
def choose_book(request, book_id, meeting_id):
    meeting = get_object_or_404(Meeting.objects, id=meeting_id)
    if request.user == meeting.chooser and not meeting.book:
        book = get_object_or_404(Book.objects, id=book_id)
        meeting.assign_book(book)

        #send email to member who has to choose a book
        MeetingHelper().send_email(request=request,
            meeting=meeting,
            subject='A book has be chosen',
            letter='emails/book_confirmation.html',
            all_mem=True
        )

        messages.add_message(request, messages.SUCCESS,
                             "Book has been chosen!")
        notify.send(meeting, recipient=meeting.club.members.all(), verb=NotificationHelper().NotificationMessages.CHOICE, action_object=book, description='club-event-B' )

        return redirect('club_page', club_id=meeting.club.id)
    else:
        raise Http404

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
    rec_helper.increment_counter()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))

class AddReviewView(LoginRequiredMixin, FormView):
    template_name = 'book_details.html'
    pk_url_kwarg = 'book_id'
    form_class = RatingForm

    # def get(self, *args, **kwargs):
    #     """Retrieves the book_id from url and stores it in self for later use."""
    #     self.book_id = self.kwargs.get('book_id', None)
    #     return super().get(self, *args, **kwargs)

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
        messages.add_message(self.request, messages.SUCCESS, 'you successfully submitted the review.')

        self.reviewed_book.calculate_average_rating()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                         "Review cannot be over 250 characters.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('book_details', kwargs = {'book_id': self.kwargs['book_id']})

"""Enable user to follow and unfollow other users."""
@login_required
def follow_toggle(request, user_id):
    current_user = request.user
    followee = get_object_or_404(User.objects, id=user_id)
    notificationHelper = NotificationHelper()

    if(not current_user.is_following(followee)):
        notificationHelper.delete_notifications(current_user, [followee], notificationHelper.NotificationMessages.FOLLOW )
        notify.send(current_user, recipient=followee, verb=notificationHelper.NotificationMessages.FOLLOW,  description='notification' )
    else:

        notificationHelper.delete_notifications(current_user, [followee], notificationHelper.NotificationMessages.FOLLOW )

    current_user.toggle_follow(followee)
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

class ShowSortedView(LoginRequiredMixin, ListView):
    template_name = 'search_page.html'
    paginate_by = settings.MEMBERS_PER_PAGE

    def post(self, *args, **kwargs):
        """Handle post request."""
        return render(self.request, 'search_page.html', {})

    def get(self, *args, **kwargs):
        """Handle get request."""
        self.searched = kwargs['searched']
        self.label = kwargs['label']
        search_page_results = get_list_of_objects(
            searched=kwargs['searched'], label=kwargs['label'])
        self.category = search_page_results["category"]
        self.filtered_list = search_page_results["filtered_list"]

        self.sortForm = ""
        if(self.category == "Clubs"):
            self.sortForm = ClubsSortForm(self.request.GET or None)
        elif(self.category == "Books"):
            self.sortForm = BooksSortForm(self.request.GET or None)
        else:
            self.sortForm = UsersSortForm(self.request.GET or None)

        sort = ""
        if (self.sortForm.is_valid()):
            sort = self.sortForm.cleaned_data.get('sort')
            sort_helper = SortHelper(sort, self.filtered_list)

            if(self.category == "Clubs"):
                self.filtered_list = sort_helper.sort_clubs()
            elif(self.category == "Books"):
                self.filtered_list = sort_helper.sort_books()
            else:
                self.filtered_list = sort_helper.sort_users()

        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Return filtered list based on search."""
        return self.filtered_list

    def get_context_data(self, **kwargs):
        """Retrieve context data to be shown on the template."""
        context = super().get_context_data(**kwargs)
        context['searched'] = self.searched
        context['label'] = self.label
        context['category'] = self.category
        context['form'] = self.sortForm
        context['filtered_list'] = context['page_obj']
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

"""Enables an owner to delete their club."""
@login_required
def delete_club(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    if(not request.user == club.owner):
        messages.add_message(request, messages.ERROR,
                             "Must be owner to delete club!")
        return redirect('club_page', club_id)

    club.delete()
    messages.add_message(request, messages.SUCCESS, "Deletion successful!")
    return redirect('home')


class MeetingsListView(LoginRequiredMixin, ListView):
    template_name = 'meetings_list.html'
    model = Meeting
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, *args, **kwargs):
        """Store user and club in self."""
        self.user = get_object_or_404(User, id=self.request.user.id)
        self.club = get_object_or_404(Club, id=kwargs['club_id'])
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Return club's upcoming meetings."""
        return self.club.get_upcoming_meetings()

    def get_context_data(self, **kwargs):
        """Retrieve context data to be shown on the template."""
        context = super().get_context_data(**kwargs)
        context['meetings_list'] = context['page_obj']
        context['user'] = self.user
        context['club'] = self.club

        return context


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)
    notification = get_object_or_404(Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return NotificationHelper().get_appropriate_redirect(notification)

class PreviousMeetingsList(LoginRequiredMixin, ListView):
    template_name = 'meetings_list.html'
    model = Meeting
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, *args, **kwargs):
        """Store user and club in self."""
        self.user = get_object_or_404(User, id=self.request.user.id)
        self.club = get_object_or_404(Club, id=kwargs['club_id'])
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Return club's previous meetings."""
        return self.club.get_previous_meetings()

    def get_context_data(self, **kwargs):
        """Retrieve context data to be shown on the template."""
        context = super().get_context_data(**kwargs)
        context['meetings_list'] = context['page_obj']
        context['user'] = self.user
        context['is_previous'] = True
        context['club'] = self.club

        return context

class ChatRoomView(LoginRequiredMixin, TemplateView):
    template_name = "chat_room.html"

    def get(self, *args, **kwargs):
        """Handle get request and perform checks on whether a user is a member
        of a club and if the club has more than one member before displaying chats. """
        user = self.request.user
        club = get_object_or_404(Club, id=kwargs['club_id']) if 'club_id' in kwargs else None

        if club:
            if not club.is_member(user) or club.members.count() <= 1:
                raise Http404
        else:
            clubs = user.clubs.all()
            if clubs:
                club = None
                for c in clubs:
                    if c.members.count() > 1:
                        club = c
                        break
                if not club:
                    messages.add_message(self.request, messages.INFO, "All your clubs have one member. Join more clubs and be part of a community.")
                    return redirect('clubs_list')
            else:
                messages.add_message(self.request, messages.INFO, "You do not have any chats! Join clubs and be part of a community.")
                return redirect('clubs_list')
        return render(self.request, "chat_room.html", {"club":club})


@login_required
def getMessages(request, club_id):
    if request.is_ajax():
        club = get_object_or_404(Club.objects, id=club_id)
        current_user = request.user

        chats = list(club.chats.all().values())[:200]
        modifiedItems = []
        for key in chats:
            user_id = key.get("user_id")
            user = get_object_or_404(User.objects, id=user_id)
            prettyDate = humanize.naturaltime(key.get("created_at").replace(tzinfo=None))
            modifiedItems.append({"name": user.full_name(), "time":prettyDate})

        return JsonResponse({"chats":chats, "modifiedItems":modifiedItems, "user_id":current_user.id})
    raise Http404

@login_required
def send(request):
    if request.method == "POST":
        message = request.POST['message']

        if message.strip():
            username = request.POST['username']
            club_id = request.POST['club_id']

            club = get_object_or_404(Club.objects, id=club_id)
            user = get_object_or_404(User.objects, username=username)

            new_chat_msg = Chat.objects.create(club=club, user=user, message=message)
            new_chat_msg.save()

        return HttpResponse('Message sent successfully')
    raise Http404

@login_required
def cancel_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting.objects, id=meeting_id)
    club = get_object_or_404(Club.objects, id=meeting.club.id)
    user = request.user

    if (user == club.owner ):
        meeting.delete()
        messages.add_message(request, messages.SUCCESS, "You cancelled the meeting successfully!")

        """send email invites"""
        MeetingHelper().send_email(request=request,
                                    meeting=meeting,
                                    subject='A meeting has been cancelled ',
                                    letter='emails/meeting_cancelation_email.html',
                                    all_mem=True)

        return redirect('meetings_list', club.id)
    else:
        messages.add_message(request, messages.ERROR, "Must be owner to cancel a meeting!")
        return redirect('meetings_list', club.id)
