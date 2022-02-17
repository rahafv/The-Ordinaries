"""Tests of the initial book list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User
from bookclub.tests.helpers import LoginRedirectTester


class InitialBookListViewTestCase(TestCase, LoginRedirectTester ):

    fixtures = ['bookclub/tests/fixtures/other_users.json' , 
                'bookclub/tests/fixtures/other_books.json'
    ]

    def setUp(self):
        self.url = reverse('initial_book_list')
        self.user = User.objects.get(id=5)
        self.other_user = User.objects.get(id=3)

    def test_initial_book_list_url(self):
        self.assertEqual(self.url,'/initial_book_list/') 

    # def test_continue_button_enabled(self):
    #      self.client.login(username=self.other_user.username, password='Password123')

    def test_show_only_first_eight_books(self):
         self.client.login(username=self.user.username, password='Password123')
         response = self.client.get(self.url)
         self.assertTemplateUsed(response, 'initial_book_list.html')

        

    def test_initial_book_list_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()



