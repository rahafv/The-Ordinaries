"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester

class HomeViewTestCase(TestCase , LogInTester):
    """Tests of the home view."""

   
    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.create_user(
        '@johndoe',
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

    def test_home_url(self):
        self.assertEqual(self.url,'/home/')

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    # def test_get_home_redirects_when_not_logged_in(self):
    #     redirect_url = self.reverse_with_next('log_in', self.url)
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)


