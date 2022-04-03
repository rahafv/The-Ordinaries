"""Unit tests for the Meeting model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import Book, Meeting
from datetime import datetime


class MeetingModelTestCase(TestCase):
    """Unit tests for the Meeting model."""

    fixtures = ['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_book.json', 
        'bookclub/tests/fixtures/other_books.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_meeting.json',
        'bookclub/tests/fixtures/other_meeting.json'
    ]
    
    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.sec_meeting = Meeting.objects.get(id=4)
        self.book = Book.objects.get(id=1)
    
    def test_valid_meeting(self):
        self._assert_meeting_is_valid()

    def test_title_can_be_200_characters_long(self):
        self.meeting.title = 'x' * 50
        self._assert_meeting_is_valid()

    def test_title_cannot_be_over_200_characters_long(self):
        self.meeting.title = 'x' * 51
        self._assert_meeting_is_invalid()

    def test_title_must_not_be_blank(self):
        self.meeting.title = ''
        self._assert_meeting_is_invalid()

    def test_title_need_not_be_unique(self):
        second_meeting = Meeting.objects.get(id=2)
        self.meeting.title = second_meeting.title
        self._assert_meeting_is_valid()

    def test_notes_cannot_be_over_500_characters_long(self):
        self.meeting.notes = 'x' * 501
        self._assert_meeting_is_invalid()
    
    def test_notes_can_be_500_characters_long(self):
        self.meeting.notes = 'x' * 500
        self._assert_meeting_is_valid()

    def test_time_must_not_be_blank(self):
        self.meeting.time = None
        self._assert_meeting_is_invalid()

    def test_time_is_valid(self):
        self.meeting.time = datetime.now()
        self._assert_meeting_is_valid()

    def test_assign_chooser(self):
        self.sec_meeting.assign_chooser()
        self._assert_meeting_is_valid()

    def test_assign_book(self):
        self.sec_meeting.assign_book(self.book)
        self._assert_meeting_is_valid()
        
    def _assert_meeting_is_valid(self):
        try:
            self.meeting.full_clean()
        except (ValidationError):
            self.fail('Test meeting should be valid')

    def _assert_meeting_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.meeting.full_clean()