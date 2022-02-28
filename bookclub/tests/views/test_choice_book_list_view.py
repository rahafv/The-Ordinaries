"""Tests of the initial book list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User , Book, Meeting
from bookclub.tests.helpers import LoginRedirectTester, MenueTestMixin


class ChoiceBookListTestCase(TestCase, LoginRedirectTester, MenueTestMixin):

    fixtures = ['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_book.json',
        'bookclub/tests/fixtures/default_meeting.json', 
        'bookclub/tests/fixtures/other_meeting.json',]  
   
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
        response = self.client.get(self.sec_url)
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'choice_book_list.html')
        self.assertEqual(len(response.context['rec_books']), 11)
        for book_id in range(10):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
        self.assert_menu(response)
        
    def test_choice_book_list_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def create_test_books(self, book_count=10):
        isbn_num = ['0425176428', '0060973129','0374157065', '0393045218', '0399135782','034545104X'
                    ,'155061224','446520802', '380000059','380711524']
        ctr = 0
        for book_id in range(book_count):
            Book.objects.create(
                ISBN = isbn_num[ctr],
                title = f'book{book_id} title',
                author = f'book{book_id} author'
            )
            ctr+=1



