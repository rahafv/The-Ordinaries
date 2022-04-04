"""Tests of the log out view."""
from bookclub.models import User
from bookclub.tests.helpers import LoginRedirectTester, LogInTester, MenuTestMixin, MessageTester
from django.test import TestCase
from django.urls import reverse


class LogOutViewTestCase(TestCase,LogInTester, LoginRedirectTester, MessageTester,MenuTestMixin):
    """Tests of the log out view."""
    
    fixtures = ['bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.get(id=1)

    def test_log_out_url(self):
        self.assertEqual(self.url,'/LogOut/')

    def test_get_log_out(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'static_templates/home.html')
        self.assertFalse(self._is_logged_in())
        self.assert_success_message(response)

    def test_get_log_out_without_being_logged_in(self):
        self.assert_redirects_when_not_logged_in()

