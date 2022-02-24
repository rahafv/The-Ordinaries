"""Unit tests of the sort form."""
from django.test import TestCase
from bookclub.models import User, Club
from bookclub.forms import ClubSortForm

class ClubSortFormTestCase(TestCase):
    """Unit tests of the review form."""

    fixtures=[
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id = 1)
        self.member = User.objects.get(id = 1)
        self.form_input = {
            'sort':ClubSortForm.DESC_DATE,
        }
    
    def test_form_has_necessary_fields(self):
        form = ClubSortForm()
        self.assertIn('sort', form.fields)

    def test_valid_sort_form(self):
        form = ClubSortForm(self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_valid_sort_form_with_updated_name_sort_field_desc(self):
        self.form_input['sort'] = ClubSortForm.DESC_NAME
        form = ClubSortForm(self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_valid_sort_form_with_updated_updated_name_sort_field_asc(self):
        self.form_input['sort'] = ClubSortForm.ASC_NAME
        form = ClubSortForm(self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_valid_sort_form_with_updated_updated_date_sort_field_desc(self):
        self.form_input['sort'] = ClubSortForm.ASC_DATE
        form = ClubSortForm(self.form_input)
        self.assertTrue(form.is_valid())



        

    