"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import SignUpForm
from bookclub.models import User
from bookclub.tests.helpers import LogInTester , MenuTestMixin
from datetime import date 

class SignUpViewTestCase(TestCase, LogInTester,MenuTestMixin):
    """Tests of the sign up view."""
    
    fixtures = ['bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'DOB': date(2000, 1, 5),
            'email': 'janedoe@example.org',
            'city': 'new york',
            'region':'NY',
            'country':'United states',
            'bio': 'Hello, this is John Doe.',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_sign_up_url(self):
        self.assertEqual(self.url,'/SignUp/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_sign_up(self):
        self.form_input['email'] = 'bademail'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_succesful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        user = User.objects.get(username='@janedoe')
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.age, 22)
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.city, 'new york')
        self.assertEqual(user.region, 'NY')
        self.assertEqual(user.country, 'United states')
        self.assertEqual(user.bio, 'Hello, this is John Doe.')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)

    def test_sign_up_log_in_prohibited(self):
        self.client.post(self.url, self.form_input)
        user = User.objects.get(id=1)
        user.email_verified = True
        self.client.login(username=user.username, password="Password123")
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        target_url = reverse("home")
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assert_menu(response)

    