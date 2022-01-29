from django.shortcuts import get_object_or_404, render , redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LogInForm, BookForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited
from .models import User, Book

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

def handler404(request,exception):
    return render(exception, '404_page.html', status=404)

def log_out(request):
    logout(request)
    return redirect('welcome')

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
def books_list(request):
    books = Book.objects.all()
    return render(request, 'books.html', {'current_user': request.user, 'books': books})
