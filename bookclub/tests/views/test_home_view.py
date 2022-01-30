"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, reverse_with_next

class HomeViewTestCase(TestCase , LogInTester):
    """Tests of the home view."""

    fixtures = ['bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('home')

    def test_home_url(self):
        self.assertEqual(self.url,'/home/')

    def test_get_home(self):
        self.client.login(username='johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_get_home_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)


