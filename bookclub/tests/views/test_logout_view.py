"""Tests of the log out view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester

class LogOutViewTestCase(TestCase,LogInTester):
    """Tests of the log out view."""

   
    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.create_user(
        'johndoe',
        first_name='John',
        last_name='Doe',
        email='johndoe@example.org',
        password='Password123',
        bio='The quick brown fox jumps over the lazy dog' , 
        age = 40 , 
        city = 'NYC' , 
        region = 'NY' , 
        country = 'USA' ,

        )


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

    def test_get_log_out_without_being_logged_in(self):
        response = self.client.get(self.url, follow=True)
        response_url = reverse('welcome')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'welcome.html')
        self.assertFalse(self._is_logged_in())
