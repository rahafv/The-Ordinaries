"""Tests of the meeting form."""
from datetime import datetime, timedelta

import pytz
from bookclub.forms import MeetingForm
from bookclub.models import Club, Meeting
from django import forms
from django.test import TestCase


class MeetingFormTestCase(TestCase):
    """Test suite for the meeting form."""

    fixtures=['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_club.json', 
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/default_book.json',
        'bookclub/tests/fixtures/other_meeting.json']

    def setUp(self):
        self.club = Club.objects.get(id=2)
        self.sec_club = Club.objects.get(id=1)
        self.meeting = Meeting.objects.get(id=2)
        self.date = pytz.utc.localize(datetime.today()+timedelta(15))

        self.form_input = {
            'title': 'meeting1',
            'time': self.date,
            'notes': 'bring the book',
            'link': 'https://goo.gl/maps/DbTzHjUu8cP4zNjRA',
            'cont': False
        }

        self.sec_form_input = {
            'title': 'meeting2',
            'time': self.date,
            'notes': 'bring the book',
            'link': 'https://goo.gl/maps/DbTzHjUu8cP4zNjRA',
            'cont': True
        }
        

    def test_valid_meeting_form(self):
        form = MeetingForm(self.club, self.form_input)
        self.assertTrue(form.is_valid())
        sec_form = MeetingForm(self.sec_club, self.sec_form_input)
        self.assertTrue(sec_form.is_valid())

    def test_form_has_correct_fields(self):
        form = MeetingForm(self.club)
        self.assertIn("title", form.fields)
        self.assertIn("time", form.fields)
        self.assertIn("notes", form.fields)
        self.assertIn("link", form.fields)
        self.assertTrue(isinstance(form.fields["time"].widget, forms.DateTimeInput))

    def test_form_model_validation(self):
        self.form_input["time"] = ""
        form = MeetingForm(self.club, self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_link_validation(self):
        self.form_input["link"] = ""
        form = MeetingForm(self.club, self.form_input)
        self.assertFalse(form.is_valid())

    def test_second_link_validation(self):
        self.form_input["link"] = ""
        form = MeetingForm(self.sec_club, self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_time_validation(self):
        self.form_input["time"] = pytz.utc.localize(datetime.today())
        form = MeetingForm(self.club, self.form_input)
        self.assertFalse(form.is_valid())

    def test_second_time_validation(self):
        self.sec_form_input["time"] = pytz.utc.localize(datetime.today())
        form = MeetingForm(self.sec_club, self.sec_form_input)
        self.assertFalse(form.is_valid())

    def test_form_meeting_validation(self):
        self.form_input["time"] = self.meeting.time
        form = MeetingForm(self.sec_club, self.form_input)
        self.assertFalse(form.is_valid())

    def test_second_meeting_validation(self):
        self.sec_form_input["time"] = self.meeting.time
        form = MeetingForm(self.sec_club, self.sec_form_input)
        self.assertFalse(form.is_valid())

    def test_no_previous_meetings(self):
        form = MeetingForm(self.club, self.sec_form_input)
        self.assertFalse(form.is_valid())

    def test_form_saves_correctly(self):
        count_clubs_before = Meeting.objects.count()
        form = MeetingForm(self.club, self.form_input)
        form.save()
        self.assertEqual(count_clubs_before + 1, Meeting.objects.count())
        meeting = Meeting.objects.get(title="meeting1")
        self.assertEqual(meeting.title, "meeting1")
        self.assertEqual(meeting.time, self.date)
        self.assertEqual(meeting.notes, "bring the book")
        self.assertEqual(meeting.link, "https://goo.gl/maps/DbTzHjUu8cP4zNjRA")
