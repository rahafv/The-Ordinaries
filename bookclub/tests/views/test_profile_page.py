"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next

class ProfilePageViewTestsCase(TestCase):
    """Tests of the profile page view."""

    fixtures = [ 'bookclub/tests/fixtures/default_user.json',]
   
    def setUp(self):
        self.url = reverse('profile')
        self.user = User.objects.get(username = "johndoe")
    
    def test_profile_page_url(self):
        self.assertEqual(self.url,'/profile/')

    def test_get_profile_page(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        menu_urls= [
            reverse('profile'), reverse('password'), reverse('log_out')
        ]
        for url in menu_urls:
            self.assertContains(response, url)    
    
    def test_get_profile_page_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)