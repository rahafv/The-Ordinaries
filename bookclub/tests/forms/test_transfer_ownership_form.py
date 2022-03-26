"""Tests of the transfer ownership form."""
from django.test import TestCase
from bookclub.forms import TransferOwnershipForm
from bookclub.models import Club, User
from django import forms

class TransferOwnershipFormTestCase(TestCase):
    """Test suite for the transfer ownership form."""

    fixtures = ['bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.url_input = {
            'club_id': '1',
            'user_id': '2'
        }
        self.form_input = {
            'new_owner': '3',
            'confirm': 'True'
        }

    def test_valid_transfer_ownership_form(self):
        form = TransferOwnershipForm(self.form_input, **self.url_input)
        self.assertTrue(form.is_valid())

    def test_form_has_correct_fields(self):
        form = TransferOwnershipForm(self.form_input, **self.url_input)
        self.assertIn("new_owner", form.fields)
        self.assertIn("confirm", form.fields)


        