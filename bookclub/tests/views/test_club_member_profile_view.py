"""Tests of the club member profile view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester,MenueTestMixin

class ProfilePageViewTestsCase(TestCase, LoginRedirectTester,MenueTestMixin):
    """Tests of the club member profile page view."""

    fixtures = [ 'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/default_club.json']
   
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.club = Club.objects.get(id=1)
        self.url = reverse('profile', kwargs={'user_id': self.user2.id, 'club_id': self.club.id})

    def test_profile_page_url(self):
        self.assertEqual(self.url,f"/club/{self.club.id}/members/{self.user2.id}")

    def test_get_member_profile(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.user2.username)    
        self.assertContains(response, self.user2.full_name())  
        self.assertNotContains(response, self.user.username)    
        self.assertNotContains(response, self.user.full_name()) 
        self.assert_menu(response)
       
    def test_get_member_profile_with_invalid_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('profile', kwargs={'user_id': self.user2.id+99999, 'club_id': self.club.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404) 

    def test_get_member_profile_with_invalid_club_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('profile', kwargs={'user_id': self.user2.id, 'club_id': self.club.id+99999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404) 

    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()