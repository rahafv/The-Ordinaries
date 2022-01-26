from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login, logout


def welcome(request):
    return render(request, 'welcome.html')


def home(request):
     return render(request, 'home.html')


def log_out(request):
    logout(request)
    return redirect('welcome')