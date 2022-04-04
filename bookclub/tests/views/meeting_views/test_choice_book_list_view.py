"""Tests of the choice book list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User , Book, Meeting
from bookclub.tests.helpers import LoginRedirectTester, MenuTestMixin, ObjectsCreator


class ChoiceBookListViewTestCase(TestCase, LoginRedirectTester, MenuTestMixin, ObjectsCreator):
    """Tests of the choice book list view."""
    
    fixtures = ['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_book.json',
        'bookclub/tests/fixtures/default_meeting.json', 
        'bookclub/tests/fixtures/other_meeting.json']  
   
    def setUp(self):
        self.meeting = Meeting.objects.get(id=1)
        self.sec_meeting = Meeting.objects.get(id=3)
        self.url = reverse('choice_book_list', kwargs={ 'meeting_id':self.meeting.id})
        self.sec_url = reverse('choice_book_list', kwargs={ 'meeting_id':self.sec_meeting.id})
        self.user = User.objects.get(id=1)
        self.sec_user = User.objects.get(id=2)

    def test_choice_book_list_url(self):
        self.assertEqual(self.url, f'/meeting/{self.meeting.id}/book_choices/') 

    def test_cant_access_when_book(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_cant_access_when_not_chooser(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)       
        
    def test_access_successful(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        self.create_test_books()
        self.book = Book.objects.get(id=1)
        self.book.add_reader(self.sec_user)
        response = self.client.get(self.sec_url)
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'meeting_templates/choice_book_list.html')
        self.assertEqual(len(response.context['rec_books']), 7)
        for book_id in range(6):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
        self.assert_menu(response)
        
    def test_choice_book_list_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()