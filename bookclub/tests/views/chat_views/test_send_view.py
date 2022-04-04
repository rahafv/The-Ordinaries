"""Tests of the send view."""
from bookclub.models import Chat, Club, User
from bookclub.tests.helpers import LoginRedirectTester, MenuTestMixin, MessageTester
from django.test import TestCase
from django.urls import reverse


class SendTest(TestCase, LoginRedirectTester, MenuTestMixin, MessageTester):
    """Tests of the send view."""

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
        self.url = reverse("send")

        self.form_input = {
            'message': 'hi',
            'username': self.user.username,
            'club_id': self.club.id,
        }

    def test_send_url(self):
        self.assertEqual(self.url, f'/send')

    def test_send_get(self):
        self.client.login(username=self.user.username, password="Password123")
        count_chats_before = Chat.objects.count()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(count_chats_before, Chat.objects.count())
 
    def test_send_successful(self):
        self.client.login(username=self.user.username, password="Password123")
        count_chats_before = Chat.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(count_chats_before + 1, Chat.objects.count())
        chat = Chat.objects.filter(message="hi")[0]
        self.assertEqual(chat.user, self.user)
        self.assertEqual(chat.club, self.club)

    def test_send_unsuccessful(self):
        self.client.login(username=self.user.username, password="Password123")
        count_chats_before = Chat.objects.count()
        self.form_input["message"] = ""
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(count_chats_before, Chat.objects.count())
        self.assertEqual(response.status_code, 200)

    def test_get_send_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_post_send_redirects_when_not_logged_in(self):
        self.assert_post_redirects_when_not_logged_in()
