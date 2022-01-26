"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User

class UserModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username = 'johndoe',
            first_name = 'John',
            last_name = 'Doe',
            age = '19',
            email = 'johndoe@example.com',
            city = 'new york',
            region = 'NY',
            country = 'United states',
            bio = 'This is john doe bio',
        )

    def test_valid_user(self):
        self._assert_user_is_valid()

    def test_username_cannot_be_blank(self):
        self.user.username = ''
        self._assert_user_is_invalid()

    def test_username_can_be_30_characters_long(self):
        self.user.username = 'x' * 30
        self._assert_user_is_valid()

    def test_username_cannot_be_over_30_characters_long(self):
        self.user.username = 'x' * 31
        self._assert_user_is_invalid()

    def test_username_must_be_unique(self):
        self.create_second_user()
        second_user = User.objects.get(username='janedoe')
        self.user.username = second_user.username
        self._assert_user_is_invalid()

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        self.create_second_user()
        second_user = User.objects.get(username='janedoe')
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        self.create_second_user()
        second_user = User.objects.get(username='janedoe')
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        self.create_second_user()
        second_user = User.objects.get(username='janedoe')
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_age_may_be_null(self):
        self.user.age = None
        self._assert_user_is_valid()

    def test_age_may_be_blank(self):
        self.user.age = ''
        self._assert_user_is_valid()

    def test_city_may_be_blank(self):
        self.user.city = ''
        self._assert_user_is_valid()

    def test_city_need_not_be_unique(self):
        self.create_second_user()
        second_user = User.objects.get(username='janedoe')
        self.user.city = second_user.city
        self._assert_user_is_valid()

    def test_city_may_contain_50_characters(self):
        self.user.city = 'x' * 50
        self._assert_user_is_valid()

    def test_city_must_not_contain_more_than_50_characters(self):
        self.user.city = 'x' * 51
        self._assert_user_is_invalid()

    def test_region_may_be_blank(self):
        self.user.region = ''
        self._assert_user_is_valid()

    def test_region_need_not_be_unique(self):
        self.create_second_user()
        second_user = User.objects.get(username='janedoe')
        self.user.region = second_user.region
        self._assert_user_is_valid()

    def test_region_may_contain_50_characters(self):
        self.user.region = 'x' * 50
        self._assert_user_is_valid()

    def test_region_must_not_contain_more_than_50_characters(self):
        self.user.region = 'x' * 51
        self._assert_user_is_invalid()

    def test_country_may_be_blank(self):
        self.user.country = ''
        self._assert_user_is_valid()

    def test_country_need_not_be_unique(self):
        self.create_second_user()
        second_user = User.objects.get(username='janedoe')
        self.user.country = second_user.country
        self._assert_user_is_valid()

    def test_country_may_contain_50_characters(self):
        self.user.country = 'x' * 50
        self._assert_user_is_valid()

    def test_country_must_not_contain_more_than_50_characters(self):
        self.user.country = 'x' * 51
        self._assert_user_is_invalid()

    def test_bio_may_be_blank(self):
        self.user.bio = ''
        self._assert_user_is_valid()

    def test_bio_need_not_be_unique(self):
        self.create_second_user()
        second_user = User.objects.get(username='janedoe')
        self.user.bio = second_user.bio
        self._assert_user_is_valid()

    def test_bio_may_contain_300_characters(self):
        self.user.bio = 'x' * 300
        self._assert_user_is_valid()

    def test_bio_must_not_contain_more_than_300_characters(self):
        self.user.bio = 'x' * 301
        self._assert_user_is_invalid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def create_second_user(self):
        User.objects.create_user(
            username = 'janedoe',
            first_name = 'Jane',
            last_name = 'Doe',
            age = None,
            email = 'janedoe@example.com',
            city = 'new york',
            region = 'NY',
            country = 'United states',
            bio = 'This is jane doe bio',
        )