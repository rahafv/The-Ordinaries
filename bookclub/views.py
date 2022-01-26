from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login, logout
from .forms import LogInForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited

@login_prohibited
def welcome(request):
    return render(request, 'welcome.html')

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

@login_required
def home(request):
     return render(request, 'home.html')


def log_out(request):
    logout(request)
    return redirect('welcome')
