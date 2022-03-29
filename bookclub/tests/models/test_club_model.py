"""Unit tests for the Club model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Club, Meeting, Book

class ClubModelTestCase(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/other_club.json', 
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_meeting.json',
        'bookclub/tests/fixtures/other_meeting.json',
        'bookclub/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.other_club = Club.objects.get(id=2)

    def _assert_club_is_valid(self):
        try:
            self.club.full_clean()
        except (ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club.full_clean()

    def test_club_created(self):
        self.assertEqual(4, Club.objects.count())

    def test_valid_club(self):
        self._assert_club_is_valid()

    def test_name_may_be_not_unique(self):
        self.club.name = self.other_club.name
        self._assert_club_is_valid()

    def test_club_name_valid(self):
        self.club.name = "x" * 50
        self._assert_club_is_valid()

    def test_club_name_not_blank(self):
        self.club.name = ""
        self._assert_club_is_invalid()

    def test_club_name_too_long(self):
        self.club.name = "x" * 51
        self._assert_club_is_invalid()

    def test_owner_may_be_not_unique(self):
        self.club.owner = self.other_club.owner
        self._assert_club_is_valid()

    def test_club_owner_not_blank(self):
        self.club.owner = None
        self._assert_club_is_invalid()

    def test_theme_may_be_blank(self):
        self.club.theme = ''
        self._assert_club_is_valid()

    def test_theme_may_be_not_unique(self):
        self.club.theme = self.other_club.theme
        self._assert_club_is_valid()

    def test_theme_may_contain_50_characters(self):
        self.club.theme = 'x' * 100
        self._assert_club_is_valid()

    def test_theme_must_not_contain_more_than_50_characters(self):
        self.club.theme = 'x' * 101
        self._assert_club_is_invalid()

    def test_club_meeting_type(self):
        self.club.meeting_type = self.club.MeetingType.INPERSON
        self.assertEqual(self.club.meeting_type, "In-person")

    def test_club_type(self):
        self.club.club_type = self.club.ClubType.PUBLIC
        self.assertEqual(self.club.club_type, "Public")
        self.assertEqual("Public", self.club.get_club_type_display())
    
    def test_city_may_be_blank(self):
        self.club.city = ''
        self._assert_club_is_valid()

    def test_city_may_be_not_unique(self):
        self.club.city = self.other_club.city
        self._assert_club_is_valid()

    def test_city_may_contain_50_characters(self):
        self.club.city = 'x' * 50
        self._assert_club_is_valid()

    def test_city_must_not_contain_more_than_50_characters(self):
        self.club.city = 'x' * 51
        self._assert_club_is_invalid()

    def test_country_may_be_blank(self):
        self.club.country = ''
        self._assert_club_is_valid()
    
    def test_country_may_be_not_unique(self):
        self.club.country = self.other_club.country
        self._assert_club_is_valid()

    def test_country_may_contain_50_characters(self):
        self.club.country = 'x' * 50
        self._assert_club_is_valid()

    def test_country_must_not_contain_more_than_50_characters(self):
        self.club.country = 'x' * 51
        self._assert_club_is_invalid()

    def test_location(self):
        self.assertTrue(self.club.location(), 'london, uk')

    def test_member_addition(self):
        nonMember = User.objects.get(id=4)
        count = self.club.member_count()
        self.club.add_member(nonMember)
        self.assertEqual(self.club.member_count(), count+1)

    def test_change_ownership(self):
        otherMember = self.club.members.get(id=3)
        self.club.make_owner(otherMember)
        self.assertEqual(self.club.owner, otherMember)

    def test_member_addition_when_user_is_already_a_member(self):
        nonMember = User.objects.get(id=4)
        self.club.add_member(nonMember)
        count = self.club.member_count()
        self.club.add_member(nonMember)
        self.assertEqual(self.club.member_count(), count)
    
    def test_get_previous_meetings(self):
        previous_meetings = self.club.get_previous_meetings()
        self.assertEqual(len(previous_meetings), 4)

    def test_get_upcoming_meetings(self):
        upcoming_meetings = self.club.get_upcoming_meetings()
        self.assertEqual(len(upcoming_meetings), 2)

