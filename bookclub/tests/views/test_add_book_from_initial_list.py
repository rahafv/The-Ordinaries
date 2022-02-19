from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import LoginRedirectTester

class AddBookFromInitialListToListViewTestCase(TestCase, LoginRedirectTester):
    
    fixtures = ['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/default_book.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.book = Book.objects.get(ISBN='0195153448')
        self.url = reverse('add_book_from_initial_list' ,  kwargs={'book_id': self.book.id})

    def test_book_details_url(self):
        self.assertEqual(self.url, f'/initial_book_list/{self.book.id}/add_book/')

    def test_successful_book_addition(self):
        count = self.book.readers_count()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        target_url = reverse("initial_book_list", kwargs={"book_id": self.book.id})
        self.assertTemplateUsed(response, 'initial_book_list.html')
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertEqual(self.book.readers_count(), count+1)


    def test_add_to_list_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()



