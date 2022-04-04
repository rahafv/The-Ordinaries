"""Unit tests of the create club form."""
from bookclub.forms import CreateClubForm
from bookclub.models import Club, User
from django import forms
from django.test import TestCase


class CreateClubFormTestCase(TestCase):
    """Test suite for the create club form."""

    fixtures = ['bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.form_input = {
            'name': 'Club1',
            'theme': 'Fiction',
            'meeting_type': Club.MeetingType.INPERSON,
            'club_type': Club.ClubType.PUBLIC,
            'city': 'nyc', 
            'country': 'usa'
        }

    def test_valid_create_club_form(self):
        form = CreateClubForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_correct_fields(self):
        form = CreateClubForm()
        self.assertIn("name", form.fields)
        self.assertIn("theme", form.fields)
        self.assertIn("meeting_type", form.fields)
        self.assertIn("club_type", form.fields)
        self.assertIn("city", form.fields)
        self.assertIn("country", form.fields)
        self.assertTrue(isinstance(form.fields["meeting_type"].widget, forms.Select))
        self.assertTrue(isinstance(form.fields["club_type"].widget, forms.Select))


    def test_form_model_validation(self):
        self.form_input["name"] = ""
        form = CreateClubForm(self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_saves_correctly(self):
        count_clubs_before = Club.objects.count()
        form = CreateClubForm(self.form_input)
        owner = User.objects.get(username="johndoe")
        form.instance.owner = owner
        form.save()
        club = Club.objects.get(name="Club1")
        self.assertEqual(count_clubs_before + 1, Club.objects.count())
        self.assertEqual(club.name, "Club1")
        self.assertEqual(club.theme, "Fiction")
        self.assertEqual(club.meeting_type, Club.MeetingType.INPERSON)
        self.assertEqual(club.club_type, Club.ClubType.PUBLIC)
        self.assertEqual(club.city, "nyc")
        self.assertEqual(club.country, "usa")
        self.assertEqual(club.owner, owner)
