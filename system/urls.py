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
    path('send_verification/<int:user_id>', views.send_activiation_email,  name='send_verification'),
    path('activate_user/<uidb64>/<token>', views.activate_user,  name='activate'),
    path('log_in/', views.log_in, name='log_in'),
    path('home/' , views.home , name = 'home'),
    path('log_out/', views.log_out , name='log_out'),
   
    path('profile/', views.show_profile_page , name='profile'),
    path('profile/<int:user_id>', views.show_profile_page , name='profile'),
    
    path('edit_profile/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('edit_review/<int:review_id>', views.edit_review, name='edit_review'),
    path('password/',views.password, name = 'password'),
    path('create_club/', views.create_club , name='create_club'),
    path("club/<int:club_id>/", views.club_page, name="club_page"),
    
    path('add_book/', views.add_book, name ='add_book'),
    path('book/<int:book_id>/book_details', views.book_details, name ='book_details'),
    path('book/<int:book_id>/add_review', views.add_review, name ='add_review'),
    path('book/<int:book_id>/add_to_list', views.add_book_to_list, name ='add_book_to_list'),

    path('club/<int:club_id>/join_club', views.join_club, name ='join_club'),
    path('club/<int:club_id>/withdraw_club', views.withdraw_club, name ='withdraw_club'),
    path('books/', views.books_list, name ='books_list'),
    path('clubs/', views.clubs_list, name ='clubs_list'),
    path('club/<int:club_id>/books/', views.books_list, name ='books_list'),
   
    #change URL format
    path('<int:user_id>/books/', views.books_list, name ='books_list'),
    path('<int:user_id>/clubs/', views.clubs_list, name ='clubs_list'),
    path("club/<int:club_id>/members/", views.members_list, name='members_list'),
    path("club/<int:club_id>/applicants/", views.applicants_list, name='applicants_list'),
    path("club/<int:club_id>/applicants/accept/<int:user_id>", views.accept_applicant, name='accept_applicant'),
    path("club/<int:club_id>/applicants/reject/<int:user_id>", views.reject_applicant, name='reject_applicant'),
    path('club/<int:club_id>/edit_club/', views.edit_club_information, name='edit_club'),
    path('follow_toggle/<int:user_id>/', views.follow_toggle, name='follow_toggle'),
    path('club/<int:club_id>/schedule_meeting/', views.schedule_meeting, name='schedule_meeting'),
]

handler404 = 'bookclub.views.handler404'
