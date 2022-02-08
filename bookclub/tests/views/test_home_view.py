"""Tests of the Home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, LoginRedirectTester, reverse_with_next , MenueTestMixin

class HomeViewTestCase(TestCase , LogInTester, LoginRedirectTester,MenueTestMixin):
    """Tests of the Home view."""

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
        self.assert_menu(response)
    
    def test_get_home_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

