"""Tests of the verfication view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, MessageTester
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from bookclub.helpers import generate_token

class VerificationViewTestCase(TestCase, LogInTester, MessageTester):
    """Tests of the verfication view."""

    fixtures = ['bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(id=5)
        self.other_user = User.objects.get(id=2)

        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = generate_token.make_token(self.user)
        self.url = reverse('activate', kwargs={'uidb64': self.uid, 'token': self.token})

    def test_activate_url(self):
        self.assertEqual(self.url,f'/activate/{self.uid}/{self.token}/')

    def test_send_activation_url(self):
        self.url = reverse('send_activation', kwargs={'user_id': 5})
        self.assertEqual(self.url,f'/send_activation/{self.user.id}/')

    def test_only_request_user_can_send_activation_url(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('send_activation', kwargs={'user_id': self.other_user.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'static_templates/404_page.html')

    def test_succesful_verification(self):
        response = self.client.get(self.url, follow=True)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'authentication_templates/log_in.html')
        self.assert_success_message(response)

    def test_invalid_verification_link(self):
        User.objects.get(id = self.user.id).delete()
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication_templates/activate_fail.html')
        self.assertContains(response, "The link is invalid")

    def test_expired_verification_link(self):
        # link expire after opening and after 72 hours
        self.user.email_verified = True
        self.user.save()
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication_templates/activate_fail.html')
        self.assertContains(response, "The link has expired")

    def test_verification_email_is_not_sent_when_already_logged_in(self):
        self.user.email_verified = True
        self.user.save()
        self.url = reverse('send_activation', kwargs={'user_id': self.user.id})
        self.client.login(username=self.user.username,  password="Password123")
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'static_templates/home.html')
        self.assert_warning_message(response)

    def test_verification_email_shows_404page_for_non_existing_users(self):
        self.url = reverse('send_activation', kwargs={'user_id': 1})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'static_templates/404_page.html')
