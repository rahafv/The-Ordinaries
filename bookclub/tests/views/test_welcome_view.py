"""Tests for the welcome view."""
from django.test import TestCase 
from django.urls import reverse
from bookclub.tests.helpers import MenuTestMixin

class WelcomeViewTestCase(TestCase,MenuTestMixin):

    def setUp(self):
        self.url = reverse("welcome")

    def test_welcome_url(self):
        self.assertEqual(self.url, "/")

    def test_get_welcome(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "welcome.html")
        self.assert_no_menu(response)