"""Tests of the Home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Rating, User , Club , Book
from bookclub.recommender.recommendation import Recommendation
from bookclub.tests.helpers import LogInTester, LoginRedirectTester, MenuTestMixin, NotificationsTester, ObjectsCreator
from bookclub.recommender.SVDModel import SVDModel
from bookclub.helpers import rec_helper

class HomeViewTestCase(TestCase , LogInTester, LoginRedirectTester, MenuTestMixin, NotificationsTester, ObjectsCreator):
    """Tests of the Home view."""

    fixtures = ['bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/other_club.json',
                'bookclub/tests/fixtures/default_book.json',
                 'bookclub/tests/fixtures/other_books.json',
                'bookclub/tests/fixtures/default_meeting.json',
                'bookclub/tests/fixtures/default_rating.json',
                 'bookclub/tests/fixtures/other_ratings.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(id=1)
        self.second_user = User.objects.get(id=2)
        
        SVDModel(rec_helper).train(rec_helper)

        self.first_club = Club.objects.get(id=1)
        self.second_club = Club.objects.get(id=2)

        self.first_book = Book.objects.get(id=1)

    def test_home_url(self):
        self.assertEqual(self.url,'/')

    def test_get_home(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.add_book_to_all_books(self.first_book)
        self.create_test_ratings(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/home.html')
        self.assert_menu(response)
    
    def test_feed_contains_events_by_self_and_followees(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.toggle_follow(self.second_user)
        self.sendNotification(self.user, self.user, self.first_club)
        self.sendNotification(self.second_user, self.user, self.first_club)
        response = self.client.get(self.url)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.second_user.username)
        self.assert_menu(response)

    def test_updates_contains_events_related_to_clubs_user_is_member_in(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.toggle_follow(self.second_user)
        self.second_user.toggle_follow(self.user)
        self.sendNotification(self.user, self.user, self.first_club)
        response = self.client.get(self.url)
        self.assertContains(response, "test club")
        self.assertContains(response, "test user")
        self.assertContains(response, self.user.username)
        self.assert_menu(response)

    def test_home_recommendation(self):
        self.client.login(username=self.user.username, password='Password123')
        self.create_test_ratings(self.user)
        response = self.client.get(self.url)
        Recommendation(True, rec_helper).get_recommendations(response.wsgi_request, 1, user_id=self.user.id)

    def test_home_recommendation_with_invalid_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        Recommendation(True, rec_helper).get_recommendations(response.wsgi_request, 1)