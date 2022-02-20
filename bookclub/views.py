from django.http import Http404
from django.http import HttpResponseForbidden
from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LogInForm, CreateClubForm, BookForm, PasswordForm, UserForm, ClubForm, RatingForm , EditRatingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .helpers import delete_event, login_prohibited, generate_token, create_event
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Club, Book , Rating, Event, ACTION_CHOICES, ACTOR_CHOICES
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail 
from system import settings
from django.core.paginator import Paginator

@login_prohibited
def welcome(request):
    return render(request, 'welcome.html')

@login_required
def home(request):
     return render(request, 'home.html')

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
        body = render_to_string('activate.html', {
            'user': user,
            'domain': current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)}
        )
        email_from = settings.EMAIL_HOST_USER
        email_to = [user.email]

        send_mail(subject, body, email_from, email_to)

        messages.add_message(request, messages.WARNING, 'Your email needs verification!')
    else:
        messages.add_message(request, messages.WARNING, 'Email is already verified!')

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
                redirect_url = next or 'home'
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
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

@login_required
def password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            new_password = form.cleaned_data.get('new_password')
            if check_password(password, current_user.password):
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('home')
            else:
                messages.add_message(request, messages.ERROR, "Password incorrect!")
        else:
            password = form.cleaned_data.get('password')
            new_password = form.cleaned_data.get('new_password')
            password_confirmation = form.cleaned_data.get('password_confirmation')
            if new_password is None and password == password_confirmation:
                messages.add_message(request, messages.ERROR, 'Your new password cannot be the same as your current one!')
            elif new_password != None and new_password != password_confirmation:
                messages.add_message(request, messages.ERROR, 'Password confirmation does not match password!')
            else:
                messages.add_message(request, messages.ERROR, "New password does not match criteria!")
    form = PasswordForm()
    return render(request, 'password.html', {'form': form})

@login_required
def create_club(request):
    if request.method == 'POST':
        form = CreateClubForm(request.POST)
        if form.is_valid():
            club_owner = request.user
            form.instance.owner = club_owner
            club = form.save()
            create_event('U', 'C', Event.EventType.CREATE, club_owner, club)
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
            create_event('U', 'B', Event.EventType.REVIEW, review_user, book=reviewed_book)
            messages.add_message(request, messages.SUCCESS, "you successfully submitted the review.")
            return redirect('book_details', book_id=reviewed_book.id)

    messages.add_message(request, messages.ERROR, "Review cannot be over 250 characters.")
    return render(request, 'book_details.html', {'book':reviewed_book})

@login_required
def club_page(request, club_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    is_member = club.is_member(current_user)
    is_applicant = club.is_applicant(current_user)
    return render(request, 'club_page.html', {'club': club, 'meeting_type': club.get_meeting_type_display(),'club_type': club.get_club_type_display(), 'is_member': is_member, 'is_applicant': is_applicant})

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
def book_details(request, book_id) :
    book = get_object_or_404(Book.objects, id=book_id)
    form = RatingForm()
    user = request.user
    check_reader = book.is_reader(user);
    reviews = book.ratings.all().exclude(review = "").exclude( user=request.user)
    rating = book.ratings.all().filter(user = request.user)
    if rating:
        rating = rating[0]
    reviews_count = book.ratings.all().exclude(review = "").exclude( user=request.user).count()
    context = {'book': book, 'form':form,
        'rating': rating , 'reviews' :reviews ,
        'reviews_count':reviews_count, 'user': user, 'reader': check_reader}
    return render(request, "book_details.html", context)

@login_required
def show_profile_page(request, user_id = None):
    user = get_object_or_404(User.objects, id=request.user.id)
    if user_id == request.user.id:
        return redirect('profile')

    if user_id:
        user = get_object_or_404(User.objects, id=user_id)

    following = request.user.is_following(user)
    followable = (request.user != user)

    return render(request, 'profile_page.html', {'current_user': request.user ,'user': user, 'following': following, 'followable': followable})

class ProfileUpdateView(LoginRequiredMixin,UpdateView):
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
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse('profile')

@login_required
def join_club(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    user = request.user

    if club.is_member(user):
        messages.add_message(request, messages.ERROR, "Already a member of this club!")
        return redirect('club_page', club_id)


    if(club.get_club_type_display() == "Private"):
        if not club.is_applicant(user):
            club.applicants.add(user)
            messages.add_message(request, messages.SUCCESS, "You have successfully applied!")
            return redirect('club_page', club_id)
        else:
            messages.add_message(request, messages.ERROR, "Already applied, awaiting approval!")
            return redirect('club_page', club_id)

    club.members.add(user)
    create_event('U', 'C', Event.EventType.JOIN, user, club)
    messages.add_message(request, messages.SUCCESS, "Joined club!")
    return redirect('club_page', club_id)

@login_required
def withdraw_club(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    user = request.user

    if user == club.owner:
        messages.add_message(request, messages.ERROR, "Must transfer ownership before leaving club!")
        return redirect('club_page', club_id)

    if not club.is_member(user):
        messages.add_message(request, messages.ERROR, "You are not a member of this club!")
        return redirect('club_page', club_id)

    club.members.remove(user)
    delete_event('U', 'C', Event.EventType.JOIN, user, club)
    create_event('U', 'C', Event.EventType.WITHDRAW, user, club)
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

    count = books_queryset.count()
    books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
    page_number = request.GET.get('page')
    books = books_pg.get_page(page_number)
    return render(request, 'books.html', {'books': books, 'general': general, 'count': count})

@login_required
def clubs_list(request, user_id=None):
    clubs_queryset = Club.objects.all()
    general = True
    if user_id:
        clubs_queryset = User.objects.get(id=user_id).clubs.all()
        general = False

    count = clubs_queryset.count()
    clubs_pg = Paginator(clubs_queryset, settings.CLUBS_PER_PAGE)
    page_number = request.GET.get('page')
    clubs = clubs_pg.get_page(page_number)
    return render(request, 'clubs.html', {'clubs': clubs, 'general': general, 'count': count})

@login_required
def members_list(request, club_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    is_member = club.is_member(current_user)
    members_queryset = club.members.all()
    # count = members_queryset.count()
    members_pg = Paginator(members_queryset, settings.MEMBERS_PER_PAGE)
    page_number = request.GET.get('page')
    members = members_pg.get_page(page_number)
    if (is_member):
        return render(request, 'members_list.html', {'members': members, 'club': club, 'current_user': current_user })
    else:
        messages.add_message(request, messages.ERROR, "You cannot access the members list" )
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
    return render(request, 'follow_list.html', {'follow_list': follow_list, 'user': user, 'is_following': is_following, 'current_user':current_user})
    
@login_required
def followers_list(request, user_id):
    user = get_object_or_404(User.objects, id=user_id)
    is_following= False
    list = user.followers.all()
    current_user = request.user

    follow_pg = Paginator(list, settings.MEMBERS_PER_PAGE)
    page_number = request.GET.get('page')
    follow_list = follow_pg.get_page(page_number)
    return render(request, 'follow_list.html', {'follow_list': follow_list, 'user': user, 'is_following': is_following, 'current_user':current_user})
    

@login_required
def applicants_list(request, club_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id) 
    applicants = club.applicants.all()
    is_owner = (club.owner == current_user)
    if (is_owner):
        return render(request, 'applicants_list.html', {'applicants': applicants,'is_owner': is_owner, 'club': club, 'current_user': current_user })
    else:
        messages.add_message(request, messages.ERROR, "You cannot access the applicants list" )
        return redirect('club_page', club_id) 

@login_required
def accept_applicant(request, club_id, user_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    applicant = get_object_or_404(User.objects, id=user_id)
    if(current_user == club.owner):
        club.members.add(applicant)
        club.applicants.remove(applicant)
        create_event('U', 'C', Event.EventType.JOIN, applicant, club)
        messages.add_message(request, messages.SUCCESS, "Applicant accepted!")
        return redirect('applicants_list', club_id)
    else:
        messages.add_message(request, messages.ERROR, "You cannot change applicant status list" )
        return redirect('club_page', club_id)

@login_required
def reject_applicant(request, club_id, user_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    applicant = get_object_or_404(User.objects, id=user_id)
    if(current_user == club.owner):
        club.applicants.remove(applicant)
        messages.add_message(request, messages.WARNING, "Applicant rejected!")
        return redirect('applicants_list', club_id)
    else:
        messages.add_message(request, messages.ERROR, "You cannot change applicant status list" )
        return redirect('club_page', club_id)

@login_required
def edit_club_information(request, club_id):
    club = Club.objects.get(id = club_id)
    if(request.method == "POST"):
        form = ClubForm(request.POST, instance=club)
        if (form.is_valid()):
            form_owner_detail= form.save(commit=False)
            form_owner_detail.owner = request.user
            form_owner_detail.save()
            club = form.save()
            messages.add_message(request, messages.SUCCESS, "Successfully updated club information!")
            return redirect('club_page', club_id)
    else:
        form = ClubForm(instance = club)
    context = {
        'form': form,
        'club_id':club_id,
    }
    return render(request, 'edit_club_info.html', context)

@login_required
def add_book_to_list(request, book_id):
    book = get_object_or_404(Book.objects, id=book_id)
    user = request.user
    if book.is_reader(user):
        book.remove_reader(user)
        messages.add_message(request, messages.SUCCESS, "Book Removed!")
    else:
        book.add_reader(user)
        create_event('U', 'B', Event.EventType.ADD, user, book=book)
        messages.add_message(request, messages.SUCCESS, "Book Added!")
    return redirect("book_details", book.id)

@login_required
def edit_review(request, review_id ):
    review =get_object_or_404(Rating.objects , id=review_id)
    reviewed_book = get_object_or_404(Book.objects, id=review.book_id)
    review_user = request.user
    if (review_user == review.user):
        if(request.method == "POST"):
            form = EditRatingForm(data = request.POST, instance=review)
            if (form.is_valid()):
                form.instance.user = review_user
                form.instance.book = reviewed_book
                form.save(review_user, reviewed_book)
                messages.add_message(request, messages.SUCCESS, "Successfully updated your review!")
                return redirect('book_details', book_id= review.book.id)
            messages.add_message(request, messages.ERROR, "Review cannot be over 250 characters!")
        else:
            form = EditRatingForm(instance = review)
    else:
        return render(request, '404_page.html', status=404)
        #return redirect('handler404')

    return render(request, 'edit_review.html', {'form' : form , 'review_id':review.id })

@login_required
def follow_toggle(request, user_id):
    current_user = request.user
    followee = get_object_or_404(User.objects, id=user_id)
    if(not current_user.is_following(followee)):
        create_event('U', 'AU', Event.EventType.FOLLOW, current_user, action_user=followee)
    else:
        delete_event('U', 'AU', Event.EventType.FOLLOW, current_user, action_user=followee)
    current_user.toggle_follow(followee)
    return redirect('profile', followee.id)
