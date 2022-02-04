"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester

class ProfilePageViewTestsCase(TestCase, LoginRedirectTester):
    """Tests of the profile page view."""

    fixtures = [ 'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/default_club.json']
   
    def setUp(self):
        self.url = reverse('profile')
        self.user = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.club = Club.objects.get(id=1)


    def test_profile_page_url(self):
        self.assertEqual(self.url,'/profile/')

    def test_get_profile_page(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        menu_urls= [
            reverse('profile'), reverse('password'), reverse('log_out')
        ]
        for url in menu_urls:
            self.assertContains(response, url)    
    
    def test_get_valid_member_profile_page(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('profile', kwargs={'user_id': self.user2.id, 'club_id': self.club.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.user2.username)    
        self.assertContains(response, self.user2.full_name())  
        self.assertNotContains(response, self.user.username)    
        self.assertNotContains(response, self.user.full_name())    

    def test_get_member_profile_page_with_request_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('profile', kwargs={'user_id': self.user.id, 'club_id': self.club.id})
        target_url = reverse('profile')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.user.username)    
        self.assertContains(response, self.user.full_name()) 

    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()