"""system URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import: from my_app import views
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
from bookclub.views import account_views, authentication_views, book_views, chat_views, club_views, follow_views, meeting_views, static_views, user_views
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

    path('', static_views.HomeView.as_view(),  name='home'),
    path('search/', static_views.SearchPageView.as_view(), name='search_page'),
    path('search/<str:searched>/<str:label>/', static_views.ShowSortedView.as_view(), name = "show_sorted"),
    path(r'mark-as-read/(<slug>[-\w]+)', static_views.mark_as_read, name='mark_as_read'),

    path('SignUp/', authentication_views.SignUpView.as_view(),  name='sign_up'),
    path('send_activation/<int:user_id>/', authentication_views.send_activiation_email,  name='send_activation'),
    path('activate/<uidb64>/<token>/', authentication_views.ActivateUserView.as_view(),  name='activate'),
    path('LogIn/', authentication_views.LogInView.as_view(), name='log_in'),
    path('LogOut/', authentication_views.log_out , name='log_out'),

    path('profile/', account_views.ProfilePageView.as_view() , name='profile'),
    path('profile/<int:user_id>', account_views.ProfilePageView.as_view() , name='profile'),
    path('edit_profile/', account_views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('password/',account_views.PasswordView.as_view(), name = 'password'),

    path('initial_genres/', user_views.InitialGenresView.as_view(), name ='initial_genres'),
    path('initial_genres/books/', user_views.InitialBookListView.as_view(), name ='initial_book_list'),
    path('book/<int:book_id>/add_to_list/', user_views.add_book_to_list, name ='add_book_to_list'),

    path('follow/<int:user_id>/', follow_views.follow_toggle, name='follow_toggle'),
    path('<int:user_id>/follow_list/', follow_views.FollowListView.as_view(), name='follow_list'),
    
    path('add_book/', book_views.AddBookView.as_view(), name ='add_book'),
    path('books/', book_views.BookListView.as_view(), name ='books_list'),
    path('club/<int:club_id>/books/', book_views.BookListView.as_view(), name ='books_list'),
    path('<int:user_id>/books/', book_views.BookListView.as_view(), name ='books_list'),
    path('book/<int:book_id>/book_details/', book_views.BookDetailsView.as_view(), name ='book_details'),
    path('book/<int:book_id>/review/', book_views.AddReviewView.as_view(), name ='add_review'),
    path('<int:review_id>/edit/', book_views.EditReviewView.as_view(), name='edit_review'),
    path('book/<int:book_id>/post_progress', book_views.post_book_progress, name ='post_progress'),
    
    path('create_club/', club_views.CreateClubView.as_view() , name='create_club'),
    path('club/<int:club_id>/', club_views.ClubPageView.as_view(), name="club_page"),
    path('club/<int:club_id>/edit/', club_views.EditClubInformationView.as_view(), name='edit_club'),
    path('club/<int:club_id>/join/', club_views.join_club, name ='join_club'),
    path('club/<int:club_id>/withdraw/', club_views.withdraw_club, name ='withdraw_club'),
    path('clubs/', club_views.ClubsListView.as_view(), name ='clubs_list'),
    path('<int:user_id>/clubs/', club_views.ClubsListView.as_view(), name ='clubs_list'),
    path('club/<int:club_id>/members/', club_views.MembersListView.as_view(), name='members_list'),
    path('club/<int:club_id>/applicants/', club_views.ApplicantsListView.as_view(), name='applicants_list'),
    path('club/<int:club_id>/applicants/accept/<int:user_id>/', club_views.accept_applicant, name='accept_applicant'),
    path('club/<int:club_id>/applicants/reject/<int:user_id>/', club_views.reject_applicant, name='reject_applicant'),
    path('club/<int:club_id>/transfer_ownership/', club_views.TransferClubOwnershipView.as_view(), name ='transfer_ownership'),
    path('club/<int:club_id>/delete/', club_views.delete_club, name='delete_club'),

    path('club/<int:club_id>/schedule_meeting/', meeting_views.ScheduleMeetingView.as_view(), name='schedule_meeting'),
    path('meeting/<int:meeting_id>/cancel/', meeting_views.cancel_meeting, name='cancel_meeting'),
    path('meeting/<int:meeting_id>/book_choices/', meeting_views.ChoiceBookListView.as_view(), name='choice_book_list'),
    path('meeting/<int:meeting_id>/search/', meeting_views.SearchBookView.as_view(), name='search_book'),
    path('meeting/<int:meeting_id>/choose/<int:book_id>', meeting_views.choose_book, name='choose_book'),
    path('club/<int:club_id>/meetings/', meeting_views.MeetingsListView.as_view(), name='meetings_list'),
    
    path('chat_room/', chat_views.ChatRoomView.as_view(), name='chat_room'),
    path('club/<int:club_id>/chat_room/', chat_views.ChatRoomView.as_view(), name='chat_room'),
    path('getMessages/<int:club_id>/', chat_views.getMessages, name='getMessages'),
    path('send', chat_views.send, name='send'),
    ]
    
handler404 = 'bookclub.views.static_views.handler404'