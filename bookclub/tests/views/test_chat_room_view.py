from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin, MessageTester

class ChatRoomTest(TestCase, LoginRedirectTester, MenuTestMixin, MessageTester):

    fixtures=['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.user = User.objects.get(id=2)
        self.sec_user = User.objects.get(id=4)
        self.url = reverse('chat_room', kwargs={'club_id': self.club.id})
        
    def test_chat_room_url(self):
        self.assertEqual(self.url,f'/club/{self.club.id}/chat_room/')

    def test_get_chat_room(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat_room.html')
        self.assert_menu(response)
    
    def test_get_chat_room_with_no_club_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('chat_room')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat_room.html')
        self.assert_menu(response)
        
    def test_get_chat_room_for_non_members(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404_page.html')

    def test_get_chat_room_for_no_clubs(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        self.url = reverse('chat_room')
        response = self.client.get(self.url, follow=True)
        response_url = reverse('clubs_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assert_info_message(response)
        self.assert_menu(response)

    def test_get_chat_room_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()