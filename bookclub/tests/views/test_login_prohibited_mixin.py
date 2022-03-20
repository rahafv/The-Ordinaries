"""Tests of the log in prohibited mixin."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LoginRedirectTester, LogInTester

class LoginProhibitedMixinTestCase(TestCase, LoginRedirectTester, LogInTester):
    """Test suite for the log in prohibited mixin."""

    fixtures = [
        'bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse("log_in")


    def test_successful_log_in_prohibited(self):
        form_input = { 'username': 'johndoe', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('initial_genres')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        sign_up_url = reverse('sign_up')
        response = self.client.get(sign_up_url)
        target_url = reverse("home")
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)


        
