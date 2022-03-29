"""Unit tests of the sort form."""
from django.test import TestCase
from bookclub.models import User, Club
from bookclub.forms import ClubsSortForm

class NameAndDateSortFormTestCase(TestCase):
    """Unit tests of the sort form."""

    fixtures=[
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id = 1)
        self.member = User.objects.get(id = 1)
        self.form_input = {
            'sort':ClubsSortForm.DESC_NAME,
        }
    
    def test_form_has_necessary_fields(self):
        form = ClubsSortForm()
        self.assertIn('sort', form.fields)

    def test_valid_sort_form(self):
        form = ClubsSortForm(self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_valid_sort_form_with_updated_name_sort_field_desc(self):
        self.form_input['sort'] = ClubsSortForm.DESC_NAME
        form = ClubsSortForm(self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_valid_sort_form_with_updated_updated_name_sort_field_asc(self):
        self.form_input['sort'] = ClubsSortForm.ASC_NAME
        form = ClubsSortForm(self.form_input)
        self.assertTrue(form.is_valid())




        

    