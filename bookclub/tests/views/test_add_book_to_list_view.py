from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import LoginRedirectTester, MenueTestMixin, MessageTester

class AddBookToListViewTestCase(TestCase, LoginRedirectTester, MenueTestMixin, MessageTester):
    
    fixtures = ['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/default_book.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.book = Book.objects.get(ISBN='0195153448')
        self.url = reverse('add_book_to_list', kwargs={'book_id': self.book.id})

    def test_book_details_url(self):
        self.assertEqual(self.url,f'/book/{self.book.id}/add_to_list')

    def test_successful_book_addition(self):
        count = self.book.readers_count()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        target_url = reverse("book_details", kwargs={"book_id": self.book.id})
        self.assertTemplateUsed(response, 'book_details.html')
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
        self.assert_menu(response)
        self.assertEqual(self.book.readers_count(), count+1)

    def test_successful_book_removal(self):
        self.client.login(username=self.user.username, password='Password123')
        self.book.add_reader(self.user)
        count = self.book.readers_count()
        response = self.client.get(self.url, follow=True)
        target_url = reverse("book_details", kwargs={"book_id": self.book.id})
        self.assertTemplateUsed(response, 'book_details.html')
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
        self.assert_menu(response)
        self.assertEqual(self.book.readers_count(), count-1)


    def test_add_to_list_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()



