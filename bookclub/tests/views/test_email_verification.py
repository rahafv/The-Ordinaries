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

    def test_succesful_verification(self):
        response = self.client.get(self.url, follow=True)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assert_success_message(response)

    def test_invalid_verification_link(self):
        User.objects.get(id = self.user.id).delete()
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'activate-fail.html')
        self.assertContains(response, "The link is invalid")

    def test_expired_verification_link(self):
        # link expire after opening and after 72 hours
        self.user.email_verified = True
        self.user.save()
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'activate-fail.html')
        self.assertContains(response, "The link has expired")

    def test_verification_email_is_not_sent_when_already_logged_in(self):
        self.user.email_verified = True
        self.user.save()
        self.url = reverse('send_verification', kwargs={'user_id': self.user.id})
        self.client.login(username=self.user.username,  password="Password123")
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assert_warning_message(response)

    def test_verification_email_shows_404page_for_non_existing_users(self):
        self.url = reverse('send_verification', kwargs={'user_id': 1})
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404_page.html')
