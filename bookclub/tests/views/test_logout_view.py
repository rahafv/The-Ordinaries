"""Tests of the log out view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, LoginRedirectTester, MessageTester

class LogOutViewTestCase(TestCase,LogInTester, LoginRedirectTester, MessageTester):
    """Tests of the log out view."""
    
    fixtures = ['bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('log_out')

    def test_log_out_url(self):
        self.assertEqual(self.url,'/log_out/')

    def test_get_log_out(self):
        self.client.login(username='johndoe', password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('welcome')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'welcome.html')
        self.assertFalse(self._is_logged_in())
        self.assert_success_message(response)

    def test_get_log_out_without_being_logged_in(self):
        self.assert_redirects_when_not_logged_in()

