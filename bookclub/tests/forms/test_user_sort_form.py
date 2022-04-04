"""Unit tests of the sort form."""
from bookclub.forms import UsersSortForm
from bookclub.models import Club, User
from django.test import TestCase


class UserSortFormTestCase(TestCase):
    """Unit tests of the sort form."""

    fixtures=[
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id = 1)
        self.member = User.objects.get(id = 1)
        self.form_input = {
            'sort': UsersSortForm.ASCENDING,
        }
    
    def test_form_has_necessary_fields(self):
        form = UsersSortForm()
        self.assertIn('sort', form.fields)

    def test_valid_sort_form(self):
        form = UsersSortForm(self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_valid_sort_form_with_updated_field(self):
        self.form_input['sort'] = UsersSortForm.DESCENDING
        form = UsersSortForm(self.form_input)
        self.assertTrue(form.is_valid())

        

    