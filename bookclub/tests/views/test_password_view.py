"""Tests for the password view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import PasswordForm
from bookclub.models import User
from bookclub.tests.helpers import LoginRedirectTester, MessageTester

class PasswordViewTest(TestCase, LoginRedirectTester, MessageTester):
    """Test suite for the password view."""

    fixtures = ['bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='johndoe')
        self.url = reverse('password')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }
        

    def test_password_url(self):
        self.assertEqual(self.url, '/password/')

    def test_get_password(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))

    def test_succesful_password_change(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', self.user.password)
        self.assertTrue(is_password_correct)
        self.assert_success_message(response)

    def test_password_change_unsuccesful_without_correct_old_password(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)
        self.assert_error_message(response)

    def test_password_change_unsuccesful_with_new_password_eqaul_old(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['new_password'] = 'Password123'
        self.form_input['password_confirmation'] = 'Password123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)
        self.assert_error_message(response)

    def test_password_change_unsuccesful_without_password_confirmation(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['password_confirmation'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)
        self.assert_error_message(response)

    def test_password_change_unsuccesful_with_criteria_not_matched(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['new_password'] = '1234567890'
        self.form_input['password_confirmation'] = '1234567890'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)
        self.assert_error_message(response)

    def test_get_password_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()
    
    def test_post_password_redirects_when_not_logged_in(self):
       self.assert_post_redirects_when_not_logged_in()