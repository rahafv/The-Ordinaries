"""Tests of the Home view."""
from urllib import response
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User , Event , Club , Book
from bookclub.tests.helpers import LogInTester, LoginRedirectTester, reverse_with_next , MenueTestMixin

class HomeViewTestCase(TestCase , LogInTester, LoginRedirectTester,MenueTestMixin):
    """Tests of the Home view."""

    fixtures = ['bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/other_club.json',
                'bookclub/tests/fixtures/default_book.json',
                'bookclub/tests/fixtures/default_meeting.json',
                'bookclub/tests/fixtures/default_rating.json',
                'bookclub/tests/fixtures/default_user_event.json',
                'bookclub/tests/fixtures/default_club_event.json',
                'bookclub/tests/fixtures/other_club_event.json',
                'bookclub/tests/fixtures/other_user_events.json']

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
        response = self.client.get(self.url)
        self.user.toggle_follow(self.second_user)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "My first event")
        self.assertContains(response,  self.second_club.name)
        self.assertContains(response, self.second_user.username)
        self.assertContains(response, "My other user event")
        self.assert_menu(response)

    def test_updates_contains_events_related_to_clubs_user_is_member_in(self):
        self.client.login(username=self.second_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, self.first_club.name)
        self.assertContains(response, "My first club event")
        self.assertContains(response, self.first_book.title)
        self.assert_menu(response)


        



        




