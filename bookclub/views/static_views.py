from bookclub.helpers import login_prohibited
from django.shortcuts import render

@login_prohibited
def welcome(request):
    return render(request, 'welcome.html')