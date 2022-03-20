from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Club, Event, Book, Meeting, Rating

class EventTest(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/default_book.json',
        'bookclub/tests/fixtures/default_meeting.json',
        'bookclub/tests/fixtures/default_rating.json',
        'bookclub/tests/fixtures/default_user_event.json',
        'bookclub/tests/fixtures/default_club_event.json',
        'bookclub/tests/fixtures/other_club_event.json',
        'bookclub/tests/fixtures/other_user_events.json'
    ]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.club = Club.objects.get(id=1)
        self.other_club = Club.objects.get(id=2)
        self.book = Book.objects.get(id=1)
        self.meeting = Meeting.objects.get(id=1)
        self.rating = Rating.objects.get(id=1)
        self.action_user = User.objects.get(id=2)
        self.user_event = Event.objects.get(id=1)
        self.club_event = Event.objects.get(id=2)
        self.other_user_event = Event.objects.get(id=3)
        self.other_user_event_action_user = Event.objects.get(id=4)
        self.other_club_event =Event.objects.get(id=5)

    def test_save_method(self):
        self.user_event.type_of_action = 'B'
        self.user_event.book = self.book
        self.user_event.save()

    def test_valid_user_event_message(self):
        try:
            self.user_event.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_valid_club_event_message(self):
        try:
            self.club_event.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_user_event_user_must_not_be_blank(self):
        self.user_event.user = None
        self._assert_event_is_invalid(self.user_event)
           
    def test_club_event_club_must_not_be_blank(self):
        self.club_event.club= None
        self._assert_event_is_invalid(self.club_event)

    def test_user_event_club_action_must_not_be_blank(self):
        self.user_event.club = None
        self._assert_event_is_invalid(self.user_event)

    def test_club_event_book_action_must_not_be_blank(self):
        self.club_event.book= None
        self._assert_event_is_invalid(self.club_event)

    def test_club_event_meeting_action_must_not_be_blank(self):
        self.other_club_event.meeting= None
        self._assert_event_is_invalid(self.other_club_event)

    def test_user_event_rating_action_must_not_be_blank(self):
        self.other_user_event.rating = None
        self._assert_event_is_invalid(self.other_user_event)

    def test_user_event_action_user_action_must_not_be_blank(self):
        self.other_user_event_action_user.action_user = None
        self._assert_event_is_invalid(self.other_user_event_action_user)

    def test_get_actor(self):
        self.assertEqual(self.user_event.get_actor(), self.user.username)
        self.assertEqual(self.club_event.get_actor(), self.club.name)

    def test_get_action_on_club_and_book(self):
        self.assertEqual(self.user_event.get_action(), self.other_club.name)
        self.assertEqual(self.club_event.get_action(), self.book.title)

    def test_get_action_on_meeting_and_rating(self):
        self.assertEqual(self.other_user_event.get_action(), self.rating.book.title)
        self.assertEqual(self.other_club_event.get_action(), self.meeting.title)

    def test_get_action_on_action_user(self):
        self.assertEqual(self.other_user_event_action_user.get_action(), self.action_user.username)

    def test_message_must_not_be_blank_for_user_event(self):
        self.user_event.message = ''
        self._assert_event_is_invalid(self.user_event)

    def test_user_event_messgae_must_not_be_overlong(self):
        self.user_event.message = 'x' * 281
        self._assert_event_is_invalid(self.user_event)

    def test_message_must_not_be_blank_for_club_event(self):
        self.club_event.message = ''
        self._assert_event_is_invalid(self.club_event)

    def test_club_event_message_must_not_be_overlong(self):
        self.club_event.message = 'x' * 281
        self._assert_event_is_invalid(self.club_event)

    def test_user_event_cannot_be_meeting(self):
        self.user_event.type_of_action= 'M'
        self.user_event.meeting = self.meeting
        self._assert_event_is_invalid(self.user_event)

    def test_club_event_cannot_be_rating(self):
        self.club_event.type_of_action= 'R'
        self.club_event.rating = self.rating
        self._assert_event_is_invalid(self.club_event)

    def test_club_event_cannot_be_club(self):
        self.club_event.type_of_action= 'C'
        self.club_event.club = self.other_club
        self._assert_event_is_invalid(self.club_event)

    def test_club_event_cannot_be_action_user(self):
        self.club_event.type_of_action= 'U'
        self.club_event.action_user = self.action_user
        self._assert_event_is_invalid(self.club_event)

    def _assert_event_is_valid(self, event):
        try:
            event.full_clean()
        except (ValidationError):
            self.fail('Test rating should be valid')

    def _assert_event_is_invalid(self, event):
        with self.assertRaises(ValidationError):
            event.full_clean()