"""Tests of the Home view."""
from urllib import response
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User , Club , Book
from bookclub.tests.helpers import LogInTester, LoginRedirectTester, reverse_with_next , MenuTestMixin, NotificationsTester

class HomeViewTestCase(TestCase , LogInTester, LoginRedirectTester,MenuTestMixin, NotificationsTester):
    """Tests of the Home view."""

    fixtures = ['bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/other_club.json',
                'bookclub/tests/fixtures/default_book.json',
                'bookclub/tests/fixtures/default_meeting.json',
                'bookclub/tests/fixtures/default_rating.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(id=1)
        self.second_user = User.objects.get(id=2)
     
        self.first_club = Club.objects.get(id=1)
        self.second_club = Club.objects.get(id=2)

        self.first_book = Book.objects.get(id=1)

    def test_home_url(self):
        self.assertEqual(self.url,'/home/')

    def test_get_home(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assert_menu(response)
    
    def test_get_home_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_feed_contains_events_by_self_and_followees(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.toggle_follow(self.second_user)
        self.sendNotification(self.user, self.user, self.first_club)
        self.sendNotification(self.second_user, self.user, self.first_club)
        self.sendNotification(self.first_club, self.user, self.first_club)
        response = self.client.get(self.url)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.second_user.username)
        self.assert_menu(response)

    def test_updates_contains_events_related_to_clubs_user_is_member_in(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.toggle_follow(self.second_user)
        self.second_user.toggle_follow(self.user)
        self.sendNotification(self.user, self.user, self.first_club)
        self.sendNotification(self.second_user, self.user, self.first_club)
        self.sendNotification(self.first_club, self.user, self.first_club)
        response = self.client.get(self.url)
        self.assertContains(response, "test club")
        self.assertContains(response, "test user")
        self.assertContains(response, self.user.username)
        self.assert_menu(response)


        



        




