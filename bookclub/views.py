from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LogInForm, CreateClubForm, BookForm, PasswordForm, UserForm, ClubForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Club, Book
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views.generic.edit import UpdateView

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
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
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

def log_out(request):
    if request.user.is_authenticated:
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
            club_owner= request.user
            form.instance.owner = club_owner
            club = form.save()
            """ adds the owner to the members list. """
            club.add_member(club_owner)
            club_owner.clubs.add(club)
            return redirect('club_page',  club_id=club.id)
    else:
        form = CreateClubForm()
    return render(request, 'create_club.html', {'form': form})

@login_required
def club_page(request, club_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    is_member = club.is_member(current_user)
    return render(request, 'club_page.html', {'club': club, 'meeting_type': club.get_meeting_type_display(), 'is_member': is_member})

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
    return render(request, "book_details.html", {'book': book})

@login_required
def show_profile_page(request):
    return render(request, 'profile_page.html')

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
    logged_in_user = request.user

    if club.is_member(logged_in_user):
        messages.add_message(request, messages.ERROR, "Already a member of this club!")
        return redirect('club_page',club_id)

    club.members.add(logged_in_user)
    logged_in_user.clubs.add(club)
    messages.add_message(request, messages.SUCCESS, "Joined club!")
    return redirect('club_page',club_id)
 
   

@login_required
def withdraw_club(request, club_id):
    
    club = get_object_or_404(Club.objects, id=club_id)
    logged_in_user = request.user

    if logged_in_user == club.owner:
        messages.add_message(request, messages.ERROR, "Must transfer ownership before leaving club!")
        return redirect('club_page',club_id)

    if not club.is_member(logged_in_user):
        messages.add_message(request, messages.ERROR, "You are not a member of this club!")
        return redirect('club_page',club_id)
    
    club.members.remove(logged_in_user)
    logged_in_user.clubs.remove(club)
    messages.add_message(request, messages.SUCCESS, "Withdrew from club!")
    return redirect('club_page',club_id)
 
    

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
        'meeting_type':club.meeting_type,
        'city': club.city,
        'country':club.country,
    }
    form = ClubForm(data) 
    context = {
        'form': form,
        'club_id':club_id,
    }
    return render(request, 'edit_club_info.html', context)

