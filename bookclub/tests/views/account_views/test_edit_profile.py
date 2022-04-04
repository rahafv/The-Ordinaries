"""Tests for the edit profile view."""
from datetime import date

from bookclub.forms import UserForm
from bookclub.models import User
from bookclub.tests.helpers import LoginRedirectTester, MenuTestMixin, MessageTester
from django.test import TestCase
from django.urls import reverse


class EditProfileViewTest(TestCase, LoginRedirectTester, MessageTester,MenuTestMixin):
    """Test suite for the edit profile view."""

    fixtures = [
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('edit_profile')
        self.user = User.objects.get(id=1)
        self.form_input = {
            'username':'johndoe2',
            'first_name': 'John2',
            'last_name': 'Doe2',
            'email':'johndoe2@example.org',
            'DOB': date(2000, 1, 5),
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
        self.assertTemplateUsed(response, 'account_templates/edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm)) 
        self.assertEqual(form.instance, self.user)
        self.assert_menu(response)

    def test_unsuccessful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = ''
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account_templates/edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')
        self.assertEqual(self.user.age, 19)
        self.assertEqual(self.user.city, 'new york')
        self.assertEqual(self.user.region, 'NY')
        self.assertEqual(self.user.country, 'United states')
        self.assertEqual(self.user.bio, "Hello, this is John Doe.")
        self.assert_menu(response)

    def test_unsuccessful_profile_update_due_to_duplicate_username(self):
        second_user = User.objects.get(id=2)       
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['username'] = second_user.username
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account_templates/edit_profile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserForm))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'johndoe@example.org')
        self.assertEqual(self.user.age, 19)
        self.assertEqual(self.user.city, 'new york')
        self.assertEqual(self.user.region, 'NY')
        self.assertEqual(self.user.country, 'United states')
        self.assertEqual(self.user.bio, "Hello, this is John Doe.")
        self.assert_menu(response)

    def test_successful_profile_update(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'account_templates/profile_page.html')
        self.assert_success_message(response)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe2')
        self.assertEqual(self.user.first_name, 'John2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.email, 'johndoe2@example.org')
        self.assertEqual(self.user.age, 22)
        self.assertEqual(self.user.city, 'Berlin')
        self.assertEqual(self.user.region, 'Berlin')
        self.assertEqual(self.user.country, 'Germany')
        self.assertEqual(self.user.bio, 'New bio')
        self.assert_menu(response)

    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()
    
    def test_post_profile_redirects_when_not_logged_in(self):
       self.assert_post_redirects_when_not_logged_in()

         