"""Test suite for the get messages view."""
from bookclub.models import Club, User
from bookclub.tests.helpers import LoginRedirectTester, MenuTestMixin, MessageTester
from django.test import TestCase
from django.urls import reverse


class GetMessagesTest(TestCase, LoginRedirectTester, MenuTestMixin, MessageTester):
    """Test suite for the get messages view."""

    fixtures=['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_club.json', 
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/default_chat.json', 
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.user = User.objects.get(id=2)
        self.non_member = User.objects.get(id=4)
        self.url = reverse("getMessages", kwargs={'club_id': self.club.id})

    def test_get_messages_url(self):
        self.assertEqual(self.url, f'/getMessages/{self.club.id}/')

    def test_get_messages_by_ajax(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, **{'HTTP_X_REQUESTED_WITH': 
        'XMLHttpRequest'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_get_messages_by_users(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_get_get_messages_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()
