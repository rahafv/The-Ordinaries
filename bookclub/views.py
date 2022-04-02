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
from django.core.mail import send_mail, send_mass_mail
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








def handler404(request, exception):
    return render(exception, '404_page.html', status=404)




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


class ProfilePageView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'profile_page.html'
    pk_url_kwarg = "user_id"

    def get(self, *args, **kwargs):
        """Retrieves the user_id and is_clubs from url and stores it in self for later use."""
        self.user_id = kwargs.get('user_id', None)
        return super().get(self.request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User.objects, id=self.request.user.id)

        if self.user_id:
            user = get_object_or_404(User.objects, id=self.user_id)
            
        if self.request.GET.get('filter') == 'Reading list':
            books_queryset = User.objects.get(id=user.id).books.all()
            books_count = books_queryset.count()
            books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
            page_number = self.request.GET.get('page')
            books = books_pg.get_page(page_number)
            context['items'] = books
            context['items_count'] = books_count
            context['is_clubs'] = False

        if self.request.GET.get('filter') == 'Clubs':
            clubs_queryset = User.objects.get(id=user.id).clubs.all()
            clubs_count = clubs_queryset.count()
            clubs_pg = Paginator(clubs_queryset, settings.CLUBS_PER_PAGE)
            page_number = self.request.GET.get('page')
            clubs = clubs_pg.get_page(page_number)
            context['items'] = clubs
            context['items_count'] = clubs_count
            context['is_clubs'] = True

        context['current_user'] = self.request.user
        context['user'] = user
        context['following'] = self.request.user.is_following(user)
        context['followable'] = (self.request.user != user)

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
            context["rec_books"] = get_recommender_books(self.request, True, 24, club_id=meeting.club.id)
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
        rec_helper.increment_counter()

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




class MeetingsListView(LoginRequiredMixin, ListView):
    #template_name = 'meetings_list.html'
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

    def get_template_names(self):
        """Returns a different template name if the user does not have access rights."""
        if self.club.is_member(self.user):
            return ['meetings_list.html']
        else:
            messages.add_message(self.request, messages.ERROR, "You cannot access the meetings of the club" )
            return ['club_page.html']
    

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

    def get_template_names(self):
        """Returns a different template name if the user does not have access rights."""
        
        if self.club.is_member(self.user):
            return ['meetings_list.html']
        else:
            messages.add_message(self.request, messages.ERROR, "You cannot access the meetings of the club" )
            return ['club_page.html']

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
    pk_url_kwarg = "club_id"

    def get(self, *args, **kwargs):
        """Handle get request and perform checks on whether a user is a member
        of a club and if the club has more than one member before displaying chats. """
        user = self.request.user
        club = get_object_or_404(Club, id=kwargs['club_id']) if 'club_id' in kwargs else None

        if club:
            if not club.is_member(user):
                raise Http404

            if club.members.count() <= 1:
                messages.add_message(self.request, messages.INFO, "This club have one member only. More members should join to start a conversation")
                return redirect('club_page' , club_id = club.id)
                
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
