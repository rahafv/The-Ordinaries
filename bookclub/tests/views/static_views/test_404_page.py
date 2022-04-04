"""Tests of the handler404 view."""
from django.test import TestCase

class handler404ViewTestCase(TestCase):
    """Tests of the 404 handler view."""

    def setUp(self):
        self.url = '/home/9999/'

    def test_get_404_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'static_templates/404_page.html')