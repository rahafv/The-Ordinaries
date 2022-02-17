"""Tests of the initial book list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LogInTester, reverse_with_next 

class InitialBookListViewTestCase(TestCase, LogInTester ):

    fixtures = ['bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.url = reverse('initial_book_list')
        self.user = User.objects.get(id=5)

    def test_initial_book_list_url(self):
        self.assertEqual(self.url,'/initial_book_list/')

