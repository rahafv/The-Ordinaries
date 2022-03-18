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
from django.urls import path, include
from bookclub import views
from django.conf.urls import url , handler404
from django.conf import settings
from django.views.static import serve
import notifications.urls


urlpatterns = [
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),


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
    path('profile/<int:user_id>/reading_list', views.show_profile_page_reading_list, name='profile_reading_list'),
    path('profile/<int:user_id>/clubs', views.show_profile_page_clubs, name='profile_clubs'),
    path('profile/<int:user_id>/<is_clubs>', views.show_profile_page , name='profile'),

    path('edit_profile/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('edit_review/<int:review_id>', views.edit_review, name='edit_review'),
    path('password/',views.PasswordView.as_view(), name = 'password'),
    path('create_club/', views.create_club , name='create_club'),
    path("club/<int:club_id>/", views.club_page, name="club_page"),

    path('add_book/', views.add_book, name ='add_book'),
    path('book/<int:book_id>/book_details', views.book_details, name ='book_details'),
    path('book/<int:book_id>/add_review', views.add_review, name ='add_review'),
    path('initial_book_list/', views.initial_book_list, name ='initial_book_list'),
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
    path('club/<int:club_id>/transfer_ownership/', views.transfer_club_ownership, name ='transfer_ownership'),
    path('follow_toggle/<int:user_id>/', views.follow_toggle, name='follow_toggle'),
    path('followings/<int:user_id>/', views.following_list, name='following_list'),
    path('followers/<int:user_id>/', views.followers_list, name='followers_list'),
    path('search_page', views.search_page, name='search_page'),  
    path('search_page/<str:searched>/<str:label>/', views.show_sorted, name = "show_sorted"), 
    path('delete_club/<int:club_id>', views.delete_club, name='delete_club'),
    path('club/<int:club_id>/schedule_meeting/', views.schedule_meeting, name='schedule_meeting'),
    path('meeting/<int:meeting_id>/book_choices/', views.choice_book_list, name='choice_book_list'),
    path('meeting/<int:meeting_id>/search/', views.search_book, name='search_book'),
    path('meeting/<int:meeting_id>/choose/<int:book_id>', views.choose_book, name='choose_book'),
    path("club/<int:club_id>/meetings/", views.meetings_list, name='meetings_list'),
    path("club/<int:club_id>/previous_meetings/", views.previous_meetings_list, name='previous_meetings_list'),
    path(r'mark-as-read/(<slug>[-\w]+)', views.mark_as_read, name='mark_as_read'),
]

handler404 = 'bookclub.views.handler404'
