from django.test import TestCase
from django.urls import reverse
from bookclub.models import Book, Club, Meeting, User
from bookclub.tests.helpers import LoginRedirectTester, MessageTester

class ChooseBookViewTest(TestCase, LoginRedirectTester, MessageTester):

    fixtures=['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_book.json',
        'bookclub/tests/fixtures/default_meeting.json', 
        'bookclub/tests/fixtures/other_meeting.json']  

    def setUp(self):
        self.meeting = Meeting.objects.get(id=3)
        self.sec_meeting = Meeting.objects.get(id=1)
        self.user = User.objects.get(id=2)
        self.sec_user = User.objects.get(id=1)
        self.book = Book.objects.get(id=1)
        self.club = Club.objects.get(id=1)
        self.url = reverse('choose_book', kwargs={'book_id':self.book.id, 'meeting_id':self.meeting.id})
        self.sec_url = reverse('choose_book', kwargs={'book_id':self.book.id, 'meeting_id':self.sec_meeting.id})


    def test_choose_book_url(self):
        self.assertEqual(self.url, f'/meeting/{self.meeting.id}/choose/{self.book.id}')

    def test_cant_access_when_book(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        response = self.client.get(self.sec_url)
        self.assertEqual(response.status_code, 404)

    def test_cant_access_when_not_chooser(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.sec_url)
        self.assertEqual(response.status_code, 404)

    def test_choose_book_successful(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertNotEqual(self.meeting.book, self.book)
        response = self.client.get(self.url)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "emails/book_confirmation.html")
        self.meeting.refresh_from_db()
        self.assertEqual(self.meeting.book, self.book)