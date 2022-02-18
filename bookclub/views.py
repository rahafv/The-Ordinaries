from datetime import datetime, timedelta
import json
from django.http import Http404, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import MeetingForm, SignUpForm, LogInForm, CreateClubForm, BookForm, PasswordForm, UserForm, ClubForm, RatingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited, generate_token
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Club, Book , Rating
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage 
from system import settings
import requests
from dateutil import tz, parser
from .auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_token
from .graph_helper import *

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
        email_subject = 'Activate your account'
        email_body = render_to_string('activate.html', {
            'user': user,
            'domain': current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)}
        )

        email = EmailMessage(subject=email_subject, body=email_body, 
        from_email=settings.EMAIL_HOST_USER, to=[user.email])

        email.send()
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
    remove_user_and_token(request)
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
            messages.add_message(request, messages.SUCCESS, "you successfully submitted the review.")
            return redirect('book_details', book_id=reviewed_book.id)

    messages.add_message(request, messages.SUCCESS, "you successfully submitted the review.")

    return render(request, 'book_details.html', {'book':reviewed_book})

@login_required
def club_page(request, club_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    is_member = club.is_member(current_user)
    return render(request, 'club_page.html', {'club': club, 'is_member': is_member})

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
    form = RatingForm()
    reviews = book.ratings.all().exclude(review = "").exclude( user=request.user)
    rating = book.ratings.all().filter(user = request.user)
    if rating:
        rating = rating[0]
    reviews_count = book.ratings.all().exclude(review = "").exclude( user=request.user).count()
    return render(request, "book_details.html", {'book': book, 'form':form, 'rating': rating , 'reviews' :reviews , 'reviews_count':reviews_count})

@login_required
def show_profile_page(request, user_id = None, club_id = None):
    user = get_object_or_404(User.objects, id=request.user.id)
    club = None
    
    if user_id == request.user.id:
        return redirect('profile') 
    
    if user_id and club_id:
        user = get_object_or_404(User.objects, id=user_id)
        club = get_object_or_404(Club.objects, id=club_id)

    return render(request, 'profile_page.html', {'current_user': request.user ,'user': user, 'club': club})

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

    club.members.add(user)
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
    messages.add_message(request, messages.SUCCESS, "Withdrew from club!")
    return redirect('club_page', club_id)

@login_required
def books_list(request, club_id=None, user_id=None):
    books = Book.objects.all()
    general = True
    if club_id:
        books = Club.objects.get(id=club_id).books.all()
        general = False
    if user_id:
        books = User.objects.get(id=user_id).books.all()
        general = False
        
    return render(request, 'books.html', {'books': books, 'general': general})

@login_required
def clubs_list(request, user_id=None):
    clubs = Club.objects.all()
    general = True
    if user_id:
        clubs = User.objects.get(id=user_id).clubs.all()
        general = False
    return render(request, 'clubs.html', {'clubs': clubs, 'general': general})

@login_required
def members_list(request, club_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    is_member = club.is_member(current_user)
    members = club.members.all()
    if (is_member):
        return render(request, 'members_list.html', {'members': members, 'is_member': is_member, 'club': club, 'current_user': current_user })
    else:
        messages.add_message(request, messages.ERROR, "You cannot access the members list" )
        return redirect('club_page', club_id)

# def reviews_list(request,rating_id,book_id):
#     ratings = Rating.objects.all()
    


@login_required
def edit_club_information(request, club_id):
    club = Club.objects.get(id = club_id)
    if (request.method == 'GET'):
        form = ClubForm(instance = club) 
        context = {
            'form': form,
            'club_id':club_id,
        }
        return render(request, 'edit_club_info.html', context)

    elif (request.method == 'POST'):
        form = ClubForm(request.POST, instance=club)
        if (form.is_valid()):
            form_owner_detail= form.save(commit=False)
            form_owner_detail.owner = request.user
            form_owner_detail.save()
            club = form.save()
            messages.add_message(request, messages.SUCCESS, "Successfully updated club information!")
            return redirect('club_page', club_id)
            
    data = {
        'name':club.name,
        'theme': club.theme,
        'city': club.city,
        'country':club.country,
    }
    form = ClubForm(data) 
    context = {
        'form': form,
        'club_id':club_id,
    }
    return render(request, 'edit_club_info.html', context)

def auth(request):
    # Get the sign-in flow
    flow = get_sign_in_flow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(flow['auth_uri'])

def callback(request):
  # Make the token request
  result = get_token_from_code(request)

  #Get the user's profile
  user = get_user(result['access_token'])

  # Store user
  store_user(request, user)
  return HttpResponseRedirect(reverse('home'))

def initialize_context(request):
  context = {}

  # Check for any errors in the session
  error = request.session.pop('flash_error', None)

  if error != None:
    context['errors'] = []
    context['errors'].append(error)

  # Check for user in the session
  context['user'] = request.session.get('user', {'is_authenticated': False})
  return context
  
def calendar(request):
    context = initialize_context(request)
    user = context['user']

    # Load the user's time zone
    # Microsoft Graph can return the user's time zone as either
    # a Windows time zone name or an IANA time zone identifier
    # Python datetime requires IANA, so convert Windows to IANA
    time_zone = get_iana_from_windows(user['timeZone'])
    tz_info = tz.gettz(time_zone)

    # Get midnight today in user's time zone
    today = datetime.now(tz_info).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    # Based on today, get the start of the week (Sunday)
    if (today.weekday() != 6):
        start = today - timedelta(days=today.isoweekday())
    else:
        start = today

    end = start + timedelta(days=7)

    token = get_token(request)

    events = get_calendar_events(
        token,
        start.isoformat(timespec='seconds'),
        end.isoformat(timespec='seconds'),
        user['timeZone']
    )

    context['errors'] = [
        { 'message': 'Events', 'debug': format(events)}
    ]

    return render(request, 'tutorial/home.html', context)

# def base64_encode(message):
#     import base64
#     message_bytes = message.encode('ascii')
#     base64_bytes = base64.b64encode(message_bytes)
#     base64_message = base64_bytes.decode('ascii')
#     return base64_message

# def zoom_auth(request):
#     code = request.GET["code"]
#     data = requests.post(f"https://zoom.us/oauth/token?grant_type=authorization_code&code={code}&redirect_uri=http://localhost:8000/zoom/auth/", headers={
#         "Authorization": "Basic " + base64_encode("5V2wX24dRMyeT2ukdlGNxw:f9Lu9GTbWd5blxs6MJxxeVhAsZZStKxw")
#     })
#     print(data.text)
#     request.session["zoom_access_token"] = data.json()["access_token"]
#     return redirect('schedule_meeting')

# def schedule_meeting(request, club_id):
#     club = get_object_or_404(Club.objects, id=club_id)
    
#     if request.method == 'POST':
#         form = MeetingForm(club, request.POST)
        
#         if form.is_valid():
#             invitees = []
#             for mem in club.members.all():
#                 invitees.append({"email": mem.email})

#             data = requests.post("https://api.zoom.us/v2/users/me/meetings", 
#                 headers={
#                     'content-type': "application/json",
#                     "authorization": f"Bearer {request.session['zoom_access_token']}"
#                 }, 
#                 data=json.dumps({
#                     "topic": f"{club.name} discussion",
#                     "type": 2,
#                     "start_time": request.POST["time"],
#                     "settings": {
#                         "meeting_invitees": invitees,
#                         "registrants_email_notification": True,
#                         "registrants_confirmation_email": True,
#                     }
#                 })
#             )
#             form.save(data.json()["start_url"], data.json()["join_url"])
#             return redirect('club_page', club_id=club.id)

#     else:
#         form = MeetingForm(club)
#     return render(request, 'schedule_meeting.html', {'form': form})


