"""Tests of the log in view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import LogInForm
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, MessageTester, reverse_with_next , MenuTestMixin

class LogInViewTestCase(TestCase, LogInTester, MessageTester,MenuTestMixin):
    """Tests of the log in view."""
    
    fixtures = ['bookclub/tests/fixtures/default_user.json' , 
                'bookclub/tests/fixtures/other_users.json' , 
                 'bookclub/tests/fixtures/default_book.json',
                 'bookclub/tests/fixtures/other_books.json'
    ]

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.get(id=1)
        self.other_user = User.objects.get(id=3)

    def test_log_in_url(self):
        self.assertEqual(self.url,'/LogIn/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(next)
        self.assert_no_message(response)

    def test_get_log_in_with_redirect(self):
        destination_url = reverse('home')
        self.url = reverse_with_next('log_in', destination_url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(next, destination_url)
        self.assert_no_message(response)

    def test_get_log_in_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_unsuccesful_log_in(self):
        form_input = { 'username': 'johndoe', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        self.assert_error_message(response)

    def test_log_in_with_blank_username(self):
        form_input = { 'username': '', 'password': 'Password123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        self.assert_error_message(response)

    def test_log_in_with_blank_password(self):
        form_input = { 'username': 'johndoe', 'password': '' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        self.assert_error_message(response)

    def test_unverified_log_in(self):
        self.user.email_verified = False
        self.user.save()
        form_input = { 'username': 'johndoe', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assert_error_message(response)

    def test_succesful_log_in_with_no_prev_books(self):
        form_input = { 'username': 'johndoe', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('initial_genres')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'initial_genres.html')
        self.assert_no_message(response)

    def test_succesful_log_in_with_prev_books(self):
        form_input = { 'username': 'peterpickles', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assert_no_message(response)

    def test_succesful_log_in_with_redirect_with_no_prev_books(self):
        redirect_url = reverse('initial_book_list')
        form_input = { 'username': 'johndoe', 'password': 'Password123', 'next': redirect_url }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'initial_book_list.html')
        self.assert_no_message(response)

    def test_succesful_log_in_with_redirect_with_prev_books(self):
        redirect_url = reverse('home')
        form_input = { 'username': 'peterpickles', 'password': 'Password123', 'next': redirect_url }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assert_no_message(response)

    def test_post_log_in_with_incorrect_credentials_and_redirect(self):
        redirect_url = reverse('log_in')
        form_input = { 'username': 'johndoe', 'password': 'WrongPassword123', 'next': redirect_url }
        response = self.client.post(self.url, form_input)
        next = response.context['next']
        self.assertEqual(next, redirect_url)
