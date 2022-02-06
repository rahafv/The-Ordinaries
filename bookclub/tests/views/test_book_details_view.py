from django.test import TestCase
from django.urls import reverse
from bookclub.models import User,Book
from bookclub.tests.helpers import LoginRedirectTester

class BookDetailsTest(TestCase, LoginRedirectTester):

    fixtures=['bookclub/tests/fixtures/default_book.json',
            'bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.target_book = Book.objects.get(ISBN='0195153448')
        self.user = User.objects.get(id=1)
        self.url = reverse('book_details', kwargs={'book_id': self.target_book.id})

    def test_book_details_url(self):
        self.assertEqual(self.url,f'/book/{self.target_book.id}/book_details')

    def test_get_book_details_with_valid_ISBN(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')

    def test_get_book_details_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('book_details', kwargs={'book_id': self.target_book.id+99999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_book_details_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()
