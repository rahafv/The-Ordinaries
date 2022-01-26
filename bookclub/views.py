from django.shortcuts import render, redirect
from .forms import SignUpForm
from .models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


def welcome(request):
    return render(request, 'welcome.html')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('welcome')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})