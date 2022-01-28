"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import UserForm
from bookclub.models import User
from bookclub.tests.helpers import reverse_with_next


class ProfileViewTest(TestCase):
    """Test suite for the profile view."""


    def setUp(self):
        self.url = reverse('edit_profile')
        self.user = User.objects.create_user(
            username = "johnd",
            first_name = "John",
            last_name = "Doe",
            email = "johndoe@example.org",
            age = 21,
            bio = "Hello, I'm John Doe.",
            city = "London",
            region = "London",
            country = "England",
            password = "Password123",
        )

        self.form_input = {
            'username':'johndoe',
            'first_name': 'John2',
            'last_name': 'Doe2',
            'email':'johndoe2@example.org',
            'age': 22,
            'bio': 'New bio',
            'city':'Berlin',
            'region':'Berlin',
            'country':'Germany',
        }

    def test_profile_url(self):
        self.assertEqual(self.url, '/edit_profile/')

    def test_get_profile(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm)) 
        self.assertEqual(form.instance, self.user)

    def test_get_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = ''
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johnd')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')
        self.assertEqual(self.user.age, 21)
        self.assertEqual(self.user.city, 'London')
        self.assertEqual(self.user.region, 'London')
        self.assertEqual(self.user.country, 'England')
        self.assertEqual(self.user.bio, "Hello, I'm John Doe.")

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        self._create_second_user()
        second_user = User.objects.get(username='jd')
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = second_user.username
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johnd')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')
        self.assertEqual(self.user.age, 21)
        self.assertEqual(self.user.city, 'London')
        self.assertEqual(self.user.region, 'London')
        self.assertEqual(self.user.country, 'England')
        self.assertEqual(self.user.bio, "Hello, I'm John Doe.")

    def test_successful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.first_name, 'John2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.email, 'johndoe2@example.org')
        self.assertEqual(self.user.age, 22)
        self.assertEqual(self.user.city, 'Berlin')
        self.assertEqual(self.user.region, 'Berlin')
        self.assertEqual(self.user.country, 'Germany')
        self.assertEqual(self.user.bio, 'New bio')

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _create_second_user(self):
        User.objects.create_user(
            username = 'jd',
            first_name = 'Jane',
            last_name = 'Doe',
            age = None,
            email = 'janedoe@example.com',
            city = 'new york',
            region = 'NY',
            country = 'United states',
            bio = 'This is jane doe bio',
        )
         