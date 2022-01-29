"""Unit tests for the Club model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Club

class ClubModelTestCase(TestCase):

    fixtures = ['bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/other_club.json', 
        'bookclub/tests/fixtures/default_club.json'
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
        self.assertEqual(2, Club.objects.count())

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
        self.assertEqual(self.club.meeting_type, "IP")
        self.assertEqual(self.club.get_meeting_type_display(), "In-person")

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



