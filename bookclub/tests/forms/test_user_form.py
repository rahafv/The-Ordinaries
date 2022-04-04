"""Unit tests of the user form."""
from datetime import date

from bookclub.forms import UserForm
from bookclub.models import User
from django import forms
from django.test import TestCase


class UserFormTestCase(TestCase):
    """Unit tests of the user form."""
    fixtures = [
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.form_input = {
            'first_name': 'John2',
            'last_name': 'Doe2',
            'username': 'johndoe2',
            'email': 'johndoe2@example.org',
            'DOB': date(2001, 1, 5),
            'bio': "Hello, I'm John Doe2.",
            'city' : 'New York',
            'region' :'NY',
            'country' : 'USA',
        }
    
    
    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        self.assertIn('DOB', form.fields)
        self.assertIn('city', form.fields)
        self.assertIn('region', form.fields)
        self.assertIn('country', form.fields)

    def test_valid_user_form(self):
        form = UserForm(data = self.form_input)
        self.assertTrue(form.is_valid())


    def test_form_uses_model_validation(self):
        second_user = User.objects.get(id=2)       
        self.form_input['username'] = second_user.username
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_year_should_be_valid(self): 
        self.form_input["DOB"] = date(2021, 1, 5)
        form = UserForm(self.form_input)
        self.assertFalse(form.is_valid())

    def test_invalid_date(self):
        self.form_input['DOB'] = date(2024, 1, 5)
        form = UserForm(self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_date(self):
        self.form_input['DOB'] = None
        form = UserForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_must_save_correctly(self):
        form = UserForm(instance=self.user, data=self.form_input, user = self.user)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(self.user.username, 'johndoe2')
        self.assertEqual(self.user.first_name, 'John2')
        self.assertEqual(self.user.last_name, 'Doe2')
        self.assertEqual(self.user.email, 'johndoe2@example.org')
        self.assertEqual(self.user.age, 21)
        self.assertEqual(self.user.bio, "Hello, I'm John Doe2.")
        self.assertEqual(self.user.city, "New York")
        self.assertEqual(self.user.region, "NY")
        self.assertEqual(self.user.country, "USA")

 