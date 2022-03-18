from datetime import timedelta
from django.http import Http404, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LogInForm, CreateClubForm, BookForm, PasswordForm, UserForm, ClubForm, RatingForm , EditRatingForm, MeetingForm, BooksSortForm, UsersSortForm, ClubsSortForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .helpers import delete_event, get_list_of_objects, login_prohibited, generate_token, create_event, MeetingHelper, SortHelper, get_appropriate_redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Meeting, User, Club, Book, Rating, Event
from django.urls import reverse
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
from django.db.models.functions import Lower
from notifications.signals import notify
from notifications.utils import slug2id
from notifications.models import Notification


@login_prohibited
def welcome(request):
    return render(request, 'welcome.html')


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

@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('send_verification', user_id=user.id)
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


def send_activiation_email(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except:
        raise Http404

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


def activate_user(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
        return render(request, 'activate-fail.html', {'user': user})

    if user and generate_token.check_token(user, token):
        user.email_verified = True
        user.save()
        messages.add_message(request, messages.SUCCESS, 'Account verified!')
        return redirect(reverse('log_in'))

    return render(request, 'activate-fail.html', {'user': user})


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user and not user.email_verified:
                messages.add_message(request, messages.ERROR,
                                     "Email is not verified, please check your email inbox!")
                return render(request, 'log_in.html', {'form': form, 'next': next, 'request': request, 'user': user})

            if user:
                login(request, user)
                if len(user.books.all()) == 0:
                    redirect_url = next or 'initial_book_list'
                else:
                    redirect_url = next or 'home'
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR,
                             "The credentials provided were invalid!")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next': next})


def handler404(request, exception):
    return render(exception, '404_page.html', status=404)


@login_required
def log_out(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, "You've been logged out.")
    return redirect('welcome')


class PasswordView(LoginRequiredMixin, FormView):
    """View that handles password change requests."""

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

        messages.add_message(
            self.request, messages.SUCCESS, "Password updated!")
        return reverse('home')


@login_required
def create_club(request):
    if request.method == 'POST':
        form = CreateClubForm(request.POST)
        if form.is_valid():
            club_owner = request.user
            form.instance.owner = club_owner
            club = form.save()
            create_event('U', 'C', Event.EventType.CREATE,
                         user=club_owner, club=club)
            """ adds the owner to the members list. """
            club.add_member(club_owner)
            return redirect('club_page', club_id=club.id)
    else:
        form = CreateClubForm()
    return render(request, 'create_club.html', {'form': form})


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
def club_page(request, club_id):
    user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    is_member = club.is_member(user)
    is_applicant = club.is_applicant(user)
    upcoming_meetings = club.get_upcoming_meetings()
    try: 
        upcoming_meeting = upcoming_meetings[0]
    except:
        upcoming_meeting=None

    
    
    return render(request, 'club_page.html', {'club': club, 'is_member': is_member, 'is_applicant': is_applicant, 'upcoming_meeting': upcoming_meeting, 'user':user})


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


"""View to add link to clubs_list in user profile """
@login_required
def show_profile_page_clubs(request, user_id=None):
    user = get_object_or_404(User.objects, id=request.user.id)

    user = get_object_or_404(User.objects, id=user_id)

    following = request.user.is_following(user)
    followable = (request.user != user)

    # clubs_queryset = get_list_or_404(Club, owner = user )
    clubs_queryset = user.clubs.all()
    clubs_count = clubs_queryset.count()
    clubs_pg = Paginator(clubs_queryset, settings.CLUBS_PER_PAGE)
    page_number = request.GET.get('page')
    clubs = clubs_pg.get_page(page_number)

    return render(request, 'profile_page.html', {'current_user': request.user, 'user': user, 'following': following, 'followable': followable, 'items': clubs, 'items_count': clubs_count, 'is_clubs': True})


""" View to add link to reading_list tto user profile """
@login_required
def show_profile_page_reading_list(request, user_id):
    user = get_object_or_404(User.objects, id=request.user.id)

    user = get_object_or_404(User.objects, id=user_id)

    following = request.user.is_following(user)
    followable = (request.user != user)

    books_queryset = user.books.all()
    books_count = books_queryset.count()
    books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
    page_number = request.GET.get('page')
    books = books_pg.get_page(page_number)

    return render(request, 'profile_page.html', {'current_user': request.user, 'user': user, 'following': following, 'followable': followable, 'items': books, 'items_count': books_count, 'is_clubs': False})


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


@login_required
def join_club(request, club_id):

    club = get_object_or_404(Club.objects, id=club_id)
    user = request.user

    if club.is_member(user):
        messages.add_message(request, messages.ERROR,
                             "Already a member of this club!")
        return redirect('club_page', club_id)

    if club.club_type == "Private":
        if not club.is_applicant(user):
            club.applicants.add(user)
            notify.send(user, recipient=club.owner, verb='applied to your club', action_object=club )
            messages.add_message(request, messages.SUCCESS,
                                 "You have successfully applied!")
            return redirect('club_page', club_id)
        else:
            messages.add_message(request, messages.ERROR,
                                 "Already applied, awaiting approval!")
            return redirect('club_page', club_id)

    club.members.add(user)
    create_event('U', 'C', Event.EventType.JOIN, user, club)
    delete_event('U', 'C', Event.EventType.WITHDRAW, user, club)
    messages.add_message(request, messages.SUCCESS, "Joined club!")
    return redirect('club_page', club_id)


@login_required
def withdraw_club(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    user = request.user

    if user == club.owner:
        messages.add_message(request, messages.ERROR,
                             "Must transfer ownership before leaving club!")
        return redirect('club_page', club_id)

    if not club.is_member(user):
        messages.add_message(request, messages.ERROR,
                             "You are not a member of this club!")
        return redirect('club_page', club_id)

    club.members.remove(user)
    delete_event('U', 'C', Event.EventType.JOIN, user=user, club=club)
    create_event('U', 'C', Event.EventType.WITHDRAW, user=user, club=club)
    messages.add_message(request, messages.SUCCESS, "Withdrew from club!")
    return redirect('club_page', club_id)


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

    form = BooksSortForm(request.GET or None)
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


@login_required
def clubs_list(request, user_id=None):
    clubs_queryset = Club.objects.all()
    general = True
    if user_id:
        clubs_queryset = User.objects.get(id=user_id).clubs.all()
        general = False

    form = ClubsSortForm(request.GET or None)
    sort = ""

    if form.is_valid():
        sort = form.cleaned_data.get('sort')
        sort_helper = SortHelper(sort, clubs_queryset)
        clubs_queryset = sort_helper.sort_clubs()

    count = clubs_queryset.count()
    clubs_pg = Paginator(clubs_queryset, settings.CLUBS_PER_PAGE)
    page_number = request.GET.get('page')
    clubs = clubs_pg.get_page(page_number)
    return render(request, 'clubs.html', {'clubs': clubs, 'general': general, 'count': count, 'form': form})


@login_required
def members_list(request, club_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    is_member = club.is_member(current_user)
    members_queryset = club.members.all()
    #form to display user sorting options
    form = UsersSortForm(request.GET or None)
    sort = ""
    if form.is_valid():
        sort = form.cleaned_data.get('sort')
        sort_helper = SortHelper(sort, members_queryset)
        members_queryset = sort_helper.sort_users()

    # count = members_queryset.count()
    members_pg = Paginator(members_queryset, settings.MEMBERS_PER_PAGE)
    page_number = request.GET.get('page')
    members = members_pg.get_page(page_number)
    if (is_member):
        return render(request, 'members_list.html', {'members': members, 'club': club, 'current_user': current_user, 'form': form})
    else:
        messages.add_message(request, messages.ERROR,
                             "You cannot access the members list")
        return redirect('club_page', club_id)


@login_required
def following_list(request, user_id):
    user = get_object_or_404(User.objects, id=user_id)
    is_following = True
    list = user.followees.all()
    current_user = request.user

    follow_pg = Paginator(list, settings.MEMBERS_PER_PAGE)
    page_number = request.GET.get('page')
    follow_list = follow_pg.get_page(page_number)
    return render(request, 'follow_list.html', {'follow_list': follow_list, 'user': user, 'is_following': is_following, 'current_user': current_user})


@login_required
def followers_list(request, user_id):
    user = get_object_or_404(User.objects, id=user_id)
    is_following = False
    list = user.followers.all()
    current_user = request.user

    follow_pg = Paginator(list, settings.MEMBERS_PER_PAGE)
    page_number = request.GET.get('page')
    follow_list = follow_pg.get_page(page_number)
    return render(request, 'follow_list.html', {'follow_list': follow_list, 'user': user, 'is_following': is_following, 'current_user': current_user})


@login_required
def applicants_list(request, club_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    applicants_queryset = club.applicants.all()
    is_owner = (club.owner == current_user)
    if (is_owner):
        #Form to display sorting options for Users
        form = UsersSortForm(request.GET or None)

        sort = ""
        if form.is_valid():
            # get the value to sort by from the valid form
            sort = form.cleaned_data.get('sort')
            sort_helper = SortHelper(sort, applicants_queryset)
            applicants_queryset = sort_helper.sort_users()

        applicants_pg = Paginator(
            applicants_queryset, settings.MEMBERS_PER_PAGE)
        page_number = request.GET.get('page')
        applicants = applicants_pg.get_page(page_number)
        return render(request, 'applicants_list.html', {'applicants': applicants, 'is_owner': is_owner, 'club': club, 'current_user': current_user, 'form': form})
    else:
        messages.add_message(request, messages.ERROR,
                             "You cannot access the applicants list")
        return redirect('club_page', club_id)


@login_required
def accept_applicant(request, club_id, user_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    applicant = get_object_or_404(User.objects, id=user_id)
    if(current_user == club.owner):
        club.members.add(applicant)
        club.applicants.remove(applicant)
        create_event('U', 'C', Event.EventType.JOIN, user=applicant, club=club)
        messages.add_message(request, messages.SUCCESS, "Applicant accepted!")
        notify.send(current_user, recipient=applicant, verb='accepted you into ', action_object=club )
        return redirect('applicants_list', club_id)
    else:
        messages.add_message(request, messages.ERROR,
                             "You cannot change applicant status list")
        return redirect('club_page', club_id)


@login_required
def reject_applicant(request, club_id, user_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    applicant = get_object_or_404(User.objects, id=user_id)
    if(current_user == club.owner):
        club.applicants.remove(applicant)
        messages.add_message(request, messages.WARNING, "Applicant rejected!")
        notify.send(current_user, recipient=applicant, verb='rejected you from ', action_object=club)
        return redirect('applicants_list', club_id)
    else:
        messages.add_message(request, messages.ERROR,
                             "You cannot change applicant status list")
        return redirect('club_page', club_id)


@login_required
def transfer_club_ownership(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    user = request.user
    memberlist = club.members.all().exclude(id=user.id)
    if user != club.owner:
        messages.add_message(request, messages.ERROR,
                             "You are not permitted to access this page!")
        return redirect('club_page', club_id=club.id)
    if memberlist.count() == 0:
        messages.add_message(request, messages.WARNING,
                             "There are no other members to tranfer the club to!")
        return redirect('club_page', club_id=club.id)
    if request.method == "POST":
        selectedmember = request.POST.get('selected_member', '')
        if selectedmember != '':
            member = get_object_or_404(User.objects, id=int(selectedmember))
            club.make_owner(member)

            messages.add_message(request, messages.SUCCESS, "Ownership transferred!")
            create_event('C', 'U', Event.EventType.TRANSFER, club=club, action_user=member)
            
            current_site = get_current_site(request)
            subject = club.name + ' Club updates'
            email_from = settings.EMAIL_HOST_USER

            members_email_body = render_to_string('emails/transfer.html', {
            'owner': member,
            'domain': current_site,
            'club':club
            })

            owner_email_body = render_to_string('emails/new_owner.html', {
            'owner': member,
            'domain': current_site,
            'club':club
            })

            email_to_members = club.members.exclude(id=member.id).values_list('email', flat=True)
            email_to_owner = [member.email]

            send_mail(subject, members_email_body, email_from, email_to_members)
            send_mail(subject, owner_email_body, email_from, email_to_owner)

            return redirect('club_page', club_id = club.id)

    return render(request, 'transfer_ownership.html', {'club': club, 'user':user, 'memberlist': memberlist})


@login_required
def edit_club_information(request, club_id):
    club = Club.objects.get(id=club_id)
    if(request.method == "POST"):
        form = ClubForm(request.POST, instance=club)
        if (form.is_valid()):
            form_owner_detail = form.save(commit=False)
            form_owner_detail.owner = request.user
            form_owner_detail.save()
            club = form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Successfully updated club information!")
            return redirect('club_page', club_id)
    else:
        form = ClubForm(instance=club)
    context = {
        'form': form,
        'club_id': club_id,
        'club': club,
    }
    return render(request, 'edit_club_info.html', context)


@login_required
def schedule_meeting(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    if request.user == club.owner:
        if club.members.count() > 1:
            if request.method == 'POST':
                form = MeetingForm(club, request.POST)

                if form.is_valid():
                    meeting = form.save()

                    """send email invites"""
                    MeetingHelper().send_email(request=request,
                                               meeting=meeting,
                                               subject='A New Meeting Has Been Scheduled',
                                               letter='emails/meeting_invite.html',
                                               all_mem=True
                                               )

                    if meeting.chooser:
                        """send email to member who has to choose a book"""
                        MeetingHelper().send_email(request=request,
                                                   meeting=meeting,
                                                   subject='It Is Your Turn!',
                                                   letter='emails/chooser_reminder.html',
                                                   all_mem=False
                                                   )
                        deadline = timedelta(7).total_seconds()  # 0.00069444
                        Timer(deadline, MeetingHelper().assign_rand_book,
                              [meeting, request]).start()

                    create_event('C', 'M', Event.EventType.SCHEDULE,
                                 club=club, meeting=meeting)
                    messages.add_message(
                        request, messages.SUCCESS, "Meeting has been scheduled!")
                    return redirect('club_page', club_id=club.id)
            else:
                form = MeetingForm(club)
            return render(request, 'schedule_meeting.html', {'form': form, 'club_id': club.id})
        else:
            messages.add_message(request, messages.ERROR,
                                 "There are no members!")
            return redirect('club_page', club_id=club.id)
    else:
        return render(request, '404_page.html', status=404)


@login_required
def choice_book_list(request, meeting_id):
    meeting = get_object_or_404(Meeting.objects, id=meeting_id)
    if request.user == meeting.chooser and not meeting.book:
        read_books = meeting.club.books.all()
        my_books =  Book.objects.all().exclude(id__in = read_books)
        sorted_books = sorted(my_books, key=lambda b: (b.average_rating, b.readers_count), reverse=True)[0:24]
        return render(request, 'choice_book_list.html', {'rec_books':sorted_books, 'meeting_id':meeting.id})
    else:
        return render(request, '404_page.html', status=404)


@login_required
def search_book(request, meeting_id):
    meeting = get_object_or_404(Meeting.objects, id=meeting_id)
    if request.method == 'GET' and request.user == meeting.chooser and not meeting.book:
        searched = request.GET.get('searched', '')
        books = Book.objects.filter(title__contains=searched)

        pg = Paginator(books, settings.BOOKS_PER_PAGE)
        page_number = request.GET.get('page')
        books = pg.get_page(page_number)
        return render(request, 'choice_book_list.html', {'searched': searched, "books": books, 'meeting_id': meeting_id})
    else:
        return redirect('choice_book_list', meeting_id=meeting_id)


@login_required
def choose_book(request, book_id, meeting_id):
    meeting = get_object_or_404(Meeting.objects, id=meeting_id)
    if request.user == meeting.chooser and not meeting.book:
        book = get_object_or_404(Book.objects, id=book_id)
        meeting.assign_book(book)

        """send email to member who has to choose a book"""
        MeetingHelper().send_email(request=request,
                                   meeting=meeting,
                                   subject='A book has be chosen',
                                   letter='emails/book_confirmation.html',
                                   all_mem=True
                                   )

        messages.add_message(request, messages.SUCCESS,
                             "Book has been chosen!")
        return redirect('club_page', club_id=meeting.club.id)
    else:
        return render(request, '404_page.html', status=404)


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
def follow_toggle(request, user_id):
    current_user = request.user
    followee = get_object_or_404(User.objects, id=user_id)
    if(not current_user.is_following(followee)):
        create_event('U', 'U', Event.EventType.FOLLOW,
                     current_user, action_user=followee)
        notify.send(current_user, recipient=followee, verb='followed you' )
    else:
        delete_event('U', 'U', Event.EventType.FOLLOW,
                     current_user, action_user=followee)
        notify.send(current_user, recipient=followee, verb='unfollowed you')
    current_user.toggle_follow(followee)
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
            sortForm = ClubsSortForm(request.GET or None)
        elif(category == "Books"):
            sortForm = BooksSortForm(request.GET or None)
        else:
            sortForm = UsersSortForm(request.GET or None)

        pg = Paginator(filtered_list, settings.MEMBERS_PER_PAGE)
        page_number = request.GET.get('page')
        filtered_list = pg.get_page(page_number)
        current_user=request.user
        return render(request, 'search_page.html', {'searched': searched, 'category': category, 'label': label, "filtered_list": filtered_list, "form": sortForm, "current_user":current_user})

    else:
        return render(request, 'search_page.html', {})


@login_required
def show_sorted(request, searched, label):
    if request.method == "GET":
        search_page_results = get_list_of_objects(
            searched=searched, label=label)
        category = search_page_results["category"]
        filtered_list = search_page_results["filtered_list"]

        sortForm = ""
        if(category == "Clubs"):
            sortForm = ClubsSortForm(request.GET or None)
        elif(category == "Books"):
            sortForm = BooksSortForm(request.GET or None)
        else:
            sortForm = UsersSortForm(request.GET or None)

        sort = ""
        if (sortForm.is_valid()):
            sort = sortForm.cleaned_data.get('sort')
            sort_helper = SortHelper(sort, filtered_list)

            if(category == "Clubs"):
                filtered_list = sort_helper.sort_clubs()
            elif(category == "Books"):
                filtered_list = sort_helper.sort_books()
            else:
                filtered_list = sort_helper.sort_users()

        pg = Paginator(filtered_list, settings.MEMBERS_PER_PAGE)
        page_number = request.GET.get('page')
        filtered_list = pg.get_page(page_number)
        return render(request, 'search_page.html', {'searched': searched, 'label': label,  'category': category, 'form': sortForm, "filtered_list": filtered_list})

    else:
        return render(request, 'search_page.html', {})

@login_required
def initial_book_list(request):
    current_user = request.user
    already_selected_books = current_user.books.all()
    my_books = Book.objects.all().exclude(id__in=already_selected_books)
    list_length = len(current_user.books.all())
    sorted_books = my_books.order_by('-average_rating','-readers_count')[:8]
    return render(request, 'initial_book_list.html', {'my_books':sorted_books , 'user':current_user , 'list_length':list_length })

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


@login_required
def meetings_list(request, club_id):
    user = get_object_or_404(User.objects, id=request.user.id)
    club = get_object_or_404(Club.objects, id=club_id)
    
    
    meetings = club.get_upcoming_meetings()
    
    meetings_pg = Paginator(meetings, settings.MEMBERS_PER_PAGE)
    page_number = request.GET.get('page')
    meetings_list = meetings_pg.get_page(page_number)
    return render(request, 'meetings_list.html', {'meetings_list': meetings_list, 'user': user, 'club':club })
    
@login_required
def previous_meetings_list(request, club_id):
    user = get_object_or_404(User.objects, id=request.user.id)
    club = get_object_or_404(Club.objects, id=club_id)
    is_previous = True
    
    meetings = club.get_previous_meetings()
    
    meetings_pg = Paginator(meetings, settings.MEMBERS_PER_PAGE)
    page_number = request.GET.get('page')
    meetings_list = meetings_pg.get_page(page_number)
    return render(request, 'meetings_list.html', {'meetings_list': meetings_list, 'user': user, 'is_previous': is_previous, 'club': club })


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)
    notification = get_object_or_404(
        Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return get_appropriate_redirect(notification)

