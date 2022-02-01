"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LoginRedirectTester

class ProfilePageViewTestsCase(TestCase, LoginRedirectTester):
    """Tests of the profile page view."""

    fixtures = [ 'bookclub/tests/fixtures/default_user.json',]
   
    def setUp(self):
        self.url = reverse('profile')
        self.user = User.objects.get(id=1)
    
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
    
    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()