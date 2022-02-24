"""Unit tests of the sort form."""
from django.test import TestCase
from bookclub.models import User, Club
from bookclub.forms import SortForm

class SortFormTestCase(TestCase):
    """Unit tests of the review form."""

    fixtures=[
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id = 1)
        self.member = User.objects.get(id = 1)
        self.form_input = {
            'sort_by': SortForm.ASCENDING,
        }
    
    def test_form_has_necessary_fields(self):
        form = SortForm()
        self.assertIn('sort_by', form.fields)

    def test_valid_sort_form(self):
        form = SortForm(self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_valid_sort_form_with_updated_field(self):
        self.form_input['sort_by'] = SortForm.DESCENDING
        form = SortForm(self.form_input)
        self.assertTrue(form.is_valid())

        

    