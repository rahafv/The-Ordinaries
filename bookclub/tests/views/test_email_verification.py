from django.test import TestCase
from django.urls import reverse
from bookclub.forms import LogInForm
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, MessageTester, reverse_with_next
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from bookclub.helpers import generate_token


class VerifiactionViewTestCase(TestCase, LogInTester, MessageTester):

    fixtures = ['bookclub/tests/fixtures/other_users.json']

    def setUp(self):

        self.user = User.objects.get(id=5)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = generate_token.make_token(self.user)
        self.url = reverse('activate', kwargs={'uidb64': self.uid, 'token': self.token})

    def test_activate_url(self):
        self.assertEqual(self.url,f'/activate_user/{self.uid}/{self.token}')

    # def test_unsuccesful_log_in(self):
    #     form_input = { 'username': 'johndoe', 'password': 'WrongPassword123' }
    #     response = self.client.post(self.url, form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'log_in.html')
    #     form = response.context['form']
    #     self.assertTrue(isinstance(form, LogInForm))
    #     self.assertFalse(form.is_bound)
    #     self.assertFalse(self._is_logged_in())
    #     self.assert_error_message(response)

    def test_succesful_verification(self):
        response = self.client.get(self.url,  kwargs={'uidb64': self.uid, 'token': self.token}, follow=True)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assert_success_message(response)

    
    def test_unsuccesful_verification(self):
        response = self.client.get(self.url,  kwargs={'uidb64': self.uid, 'token': self.token}, follow=True)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assert_success_message(response)

    # def test_succesful_log_in_with_redirect(self):
    #     redirect_url = reverse('home')
    #     form_input = { 'username': 'johndoe', 'password': 'Password123', 'next': redirect_url }
    #     response = self.client.post(self.url, form_input, follow=True)
    #     self.assertTrue(self._is_logged_in())
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'home.html')
    #     self.assert_no_message(response)

    # def test_post_log_in_with_incorrect_credentials_and_redirect(self):
    #     redirect_url = reverse('log_in')
    #     form_input = { 'username': 'johndoe', 'password': 'WrongPassword123', 'next': redirect_url }
    #     response = self.client.post(self.url, form_input)
    #     next = response.context['next']
    #     self.assertEqual(next, redirect_url)