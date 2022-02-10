"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from bookclub.forms import ClubForm
from bookclub.models import User, Club


class UserFormTestCase(TestCase):
    """Unit tests of the user form."""
    fixtures = [
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id = 1)
        self.user = User.objects.get(id = self.club.owner.id)
        self.form_input = {
            'name': 'club2',
            'theme':'Drama',
            'city' : 'New York',
            'country' : 'USA',
        }
    
    def test_form_has_correct_fields(self):
        form = ClubForm()
        self.assertIn("name", form.fields)
        self.assertIn("theme", form.fields)
        self.assertIn("city", form.fields)
        self.assertIn("country", form.fields)
        
    def test_valid_club_form(self):
        form = ClubForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_model_validation(self):
        self.form_input["name"] = ""
        form = ClubForm(self.form_input)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.is_bound)
    
    def test_form_model_should_be_valid_with_duplaicate_name(self):
        second_club = Club.objects.get(id = 2)
        self.form_input["name"] = second_club.name
        form = ClubForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_must_save_correctly(self):
        before_count = Club.objects.filter(owner = self.user.id).count()
        members_before_count = self.club.member_count()
        form = ClubForm(instance=self.club, data=self.form_input)
        owner = self.user
        form.instance.owner = owner
        form.save()
        after_count = Club.objects.filter(owner = self.user.id).count()
        members_after_count = self.club.member_count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(members_after_count, members_before_count)
        self.assertEqual(self.club.name, 'club2')
        self.assertEqual(self.club.theme, 'Drama')
        self.assertEqual(self.club.city, "New York")
        self.assertEqual(self.club.country, "USA")
