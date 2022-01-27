"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from bookclub.forms import UserForm
from bookclub.models import User

class UserFormTestCase(TestCase):
    """Unit tests of the user form."""

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'janedoe@example.org',
            'age':21,
            'bio': "Hello, I'm Jane Doe.",
            'city' : 'New York',
            'region' :'NY',
            'country' : 'USA',
        }

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

    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('bio', form.fields)
        self.assertIn('age', form.fields)
        self.assertIn('city', form.fields)
        self.assertIn('region', form.fields)
        self.assertIn('country', form.fields)

    def test_valid_user_form(self):
        form = UserForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self._create_second_user()
        second_user = User.objects.get(username='jd')       
        self.form_input['username'] = second_user.username
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(username='johnd')
        form = UserForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.username, 'janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(user.age, 21)
        self.assertEqual(user.bio, "Hello, I'm Jane Doe.")
        self.assertEqual(user.city, "New York")
        self.assertEqual(user.region, "NY")
        self.assertEqual(user.country, "USA")

    
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