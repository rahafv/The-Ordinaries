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
                'bookclub/tests/fixtures/default_rating.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.club = Club.objects.get(id=1)
        self.other_club = Club.objects.get(id=2)
        self.book = Book.objects.get(id=1)
        self.meeting = Meeting.objects.get(id=1)
        self.rating = Rating.objects.get(id=1)
        self.user_event = Event(
            type_of_actor= 'U',
            type_of_action= 'C',
            user=self.user,
            club= self.other_club,
            message ="This user is alive??",
        )
        self.club_event = Event(
            type_of_actor= 'C',
            type_of_action= 'B',
            club=self.club,
            book= self.book,
            message="This is an incredible club.",
        )
        self.other_user_event = Event(
            type_of_actor= 'U',
            type_of_action= 'R',
            user=self.user,
            rating= self.rating,
            message ="This user is alive??",
        )
        self.other_club_event = Event(
            type_of_actor= 'C',
            type_of_action= 'M',
            club=self.club,
            meeting= self.meeting,
            message="This is an incredible club.",
        )

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
        with self.assertRaises(ValidationError):
            self.user_event.full_clean()
           
    def test_club_event_club_must_not_be_blank(self):
        self.club_event.club= None
        with self.assertRaises(ValidationError):
            self.club_event.full_clean()

    def test_user_event_club_action_must_not_be_blank(self):
        self.user_event.club = None
        with self.assertRaises(ValidationError):
            self.user_event.full_clean()

    def test_club_event_book_action_must_not_be_blank(self):
        self.club_event.book= None
        with self.assertRaises(ValidationError):
            self.club_event.full_clean()

    def test_club_event_meeting_action_must_not_be_blank(self):
        self.other_club_event.meeting= None
        with self.assertRaises(ValidationError):
            self.other_club_event.full_clean()

    def test_user_event_rating_action_must_not_be_blank(self):
        self.other_user_event.rating = None
        with self.assertRaises(ValidationError):
            self.other_user_event.full_clean()

    def test_get_actor(self):
        self.assertEqual(self.user_event.get_actor(), self.user.username)
        self.assertEqual(self.club_event.get_actor(), self.club.name)

    def test_get_action_on_club_and_book(self):
        self.assertEqual(self.user_event.get_action(), self.other_club.name)
        self.assertEqual(self.club_event.get_action(), self.book.title)

    def test_get_action_on_meeting_and_rating(self):
        self.assertEqual(self.other_user_event.get_action(), self.rating.book.title)
        self.assertEqual(self.other_club_event.get_action(), self.meeting.title)

    def test_message_must_not_be_blank_for_user_event(self):
        self.user_event.message = ''
        with self.assertRaises(ValidationError):
            self.user_event.full_clean()

    def test_user_event_messgae_must_not_be_overlong(self):
        self.user_event.message = 'x' * 281
        with self.assertRaises(ValidationError):
            self.user_event.full_clean()

    def test_message_must_not_be_blank_for_club_event(self):
        self.club_event.message = ''
        with self.assertRaises(ValidationError):
            self.club_event.full_clean()

    def test_club_event_message_must_not_be_overlong(self):
        self.club_event.message = 'x' * 281
        with self.assertRaises(ValidationError):
            self.club_event.full_clean()
