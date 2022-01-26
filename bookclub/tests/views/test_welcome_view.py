"""Tests for the welcome view."""
from django.test import TestCase
from django.urls import reverse


class WelcomeViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse("welcome")

    def test_welcome_url(self):
        self.assertEqual(self.url, "/")

    def test_get_welcome(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "welcome.html")