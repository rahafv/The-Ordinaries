"""Tests of the chatroom view."""
from bookclub.models import Club, User
from bookclub.tests.helpers import LoginRedirectTester, MenuTestMixin, MessageTester
from django.test import TestCase
from django.urls import reverse


class ChatRoomTest(TestCase, LoginRedirectTester, MenuTestMixin, MessageTester):
    """Tests of the chatroom view."""

    fixtures=['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_club.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.user = User.objects.get(id=2)
        self.sec_user = User.objects.get(id=6)
        self.third_user = User.objects.get(id=5)

        self.fourth_user = User.objects.get(id=4)
        self.second_club = Club.objects.get(id=4)

        self.url = reverse('chat_room', kwargs={'club_id': self.club.id})
        
    def test_chat_room_url(self):
        self.assertEqual(self.url,f'/club/{self.club.id}/chat_room/')

    def test_get_chat_room(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat_templates/chat_room.html')
        self.assert_menu(response)
    
    def test_get_chat_room_with_no_club_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('chat_room')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat_templates/chat_room.html')
        self.assert_menu(response)
        
    def test_get_chat_room_for_non_members(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'static_templates/404_page.html')

    def test_get_chat_room_for_no_clubs(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        self.url = reverse('chat_room')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('clubs_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_templates/clubs.html')
        self.assert_info_message(response)
        self.assert_menu(response)

    def test_get_chat_room_for_no_clubs_with_members(self):
        self.client.login(username=self.third_user.username, password='Password123')
        self.url = reverse('chat_room')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('clubs_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'club_templates/clubs.html')
        self.assert_info_message(response)
        self.assert_menu(response)

    def test_get_chat_room_for_clubs_with_one_member_only(self):
        self.client.login(username=self.fourth_user.username, password='Password123')
        self.url = reverse('chat_room' ,kwargs={'club_id': self.second_club.id})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_templates/club_page.html')
        self.assert_info_message(response)
        self.assert_menu(response)

    def test_get_chat_room_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()
