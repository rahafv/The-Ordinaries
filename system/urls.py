"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from bookclub import views
from django.conf.urls import url , handler404
from django.conf import settings
from django.views.static import serve


urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}),


    path('admin/', admin.site.urls),
    path('', views.welcome,  name='welcome'),
    path('sign_up/', views.sign_up,  name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('home/' , views.home , name = 'home'),
    path('log_out/', views.log_out , name='log_out'),
    path('password/',views.password, name = 'password'),
    path('create_club/', views.create_club , name='create_club'),
    path("club/<int:club_id>/", views.club_page, name="club_page"),
    path('add_book/', views.add_book, name ='add_book'),
    path('book_details/<int:book_id>', views.book_details, name ='book_details'),
    path('join_club/<int:club_id>/', views.join_club, name ='join_club'),
    path('withdraw_club/<int:club_id>/', views.withdraw_club, name ='withdraw_club')
    path('books/', views.books_list, name ='books_list'),
    path('club/<int:club_id>/books/', views.books_list, name ='books_list'),
    #change URL format
    path('<int:user_id>/books/', views.books_list, name ='books_list')
]

handler404 = 'bookclub.views.handler404'
