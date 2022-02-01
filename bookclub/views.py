from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LogInForm, CreateClubForm, BookForm, PasswordForm, UserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Club, Book
from django.contrib.auth.hashers import check_password
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
            form.instance.owner = request.user
            club = form.save()
            return redirect('club_page',  club_id=club.id)
    else:
        form = CreateClubForm()
    return render(request, 'create_club.html', {'form': form})

@login_required
def club_page(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    return render(request, 'club_page.html', {'club': club, 'meeting_type': club.get_meeting_type_display()})

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
    # club = get_object_or_404(Club.objects, id=club_id)
    general = True
    if user_id:
        clubs = User.objects.get(id=user_id).clubs.all()
        general = False
    return render(request, 'clubs.html', {'clubs': clubs, 'general': general})
