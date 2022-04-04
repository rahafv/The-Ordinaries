"""Test suite for the search page view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Meeting, User, Book
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin, ObjectsCreator

class SearchPageViewTest(TestCase, LoginRedirectTester, MenuTestMixin, ObjectsCreator):
    """Test suite for the search page view."""

    fixtures=['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_book.json',
        'bookclub/tests/fixtures/default_meeting.json', 
        'bookclub/tests/fixtures/other_meeting.json']  

    def setUp(self):
        self.meeting = Meeting.objects.get(id=3)
        self.sec_meeting = Meeting.objects.get(id=1)
        self.url = reverse('search_book', kwargs={ 'meeting_id':self.meeting.id})
        self.sec_url = reverse('search_book', kwargs={ 'meeting_id':self.sec_meeting.id})
        self.user = User.objects.get(id=2)
        self.sec_user = User.objects.get(id=1)
        self.BOOKS_PER_PAGE = 15

        self.book_title_form_input = {
            'searched':'uio',
        }

        self.empty_form_input = {
            'searched':'',
        }

    def test_search_book_url(self):
        self.assertEqual(self.url, f'/meeting/{self.meeting.id}/search/')

    def test_cant_access_when_book(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        response = self.client.get(self.sec_url)
        response_url = reverse('choice_book_list', kwargs={'meeting_id': self.sec_meeting.id})
        self.assertEqual(response.status_code, 404)

    def test_cant_access_when_not_chooser(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.sec_url)
        response_url = reverse('choice_book_list', kwargs={'meeting_id': self.sec_meeting.id})
        self.assertEqual(response.status_code, 404)

    def test_search_books_with_title(self):
        self.client.login(username=self.user.username, password='Password123')
        self.create_test_search_books()
        response = self.client.get(self.url, self.book_title_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_templates/choice_book_list.html')
        self.assertContains(response, "uio")
        self.assertNotContains(response, "xyz")
        self.assert_menu(response)

    def test_search_with_empty_str(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, self.empty_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_templates/choice_book_list.html')
        self.assertContains(response, "You forgot to search!")
        self.assert_menu(response)

    def test_choice_book_list_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()   