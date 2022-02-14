"""Tests of the logged in user profile view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LoginRedirectTester,MenueTestMixin

class ProfilePageViewTestsCase(TestCase, LoginRedirectTester,MenueTestMixin):
    """Tests of the looged in user's profile page view."""

    fixtures = [ 'bookclub/tests/fixtures/default_user.json']
   
    def setUp(self):
        self.url = reverse('logged_in_user_profile')
        self.user = User.objects.get(id=1)
       
    def test_profile_page_url(self):
        self.assertEqual(self.url,'/profile/')

    def test_get_profile_page(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        menu_urls= [
            reverse('logged_in_user_profile'), reverse('password'), reverse('log_out')
        ]
        for url in menu_urls:
            self.assertContains(response, url)  
        self.assert_menu(response)  
   
    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()