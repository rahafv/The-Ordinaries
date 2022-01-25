from django.shortcuts import render

def welcome(request):
    return render(request, 'welcome_page.html')

