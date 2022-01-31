from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Book

class BooksListTest(TestCase):

    fixtures=['bookclub/tests/fixtures/default_book.json',
                'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.target_book = Book.objects.get(ISBN='0195153448')
        self.user = User.objects.get(id=1)
        self.club = Club.objects.get(id=1)
        self.url = reverse('books_list')

    def test_books_list_url(self):
        self.assertEqual(self.url,f'/books/')

    def test_get_club_books_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('books_list', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books.html')

    def test_books_list_redirects_when_not_logged_in(self):
        redirect_url = reverse('log_in')+f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_books_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_books(6)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books.html')
        for book_id in range(6):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
            books_url = reverse('books_list')
            self.assertContains(response, books_url)

    def test_get_user_books_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_books(6)
        self.url = reverse('books_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books.html')
        self.assertContains(response, f'The book list is empty! find more book you might like.')
        self.assertContains(response, f'More books')
        books_url = reverse('books_list')
        self.assertContains(response, books_url)

    def _create_test_books(self, book_count=6):
        isbn_num = ['0425176428', '0002005018', '0060973129','0374157065', '0393045218', '0399135782']
        ctr = 0
        for book_id in range(book_count):
            book = Book.objects.create(
                ISBN = isbn_num[ctr],
                title = f'book{book_id} title',
                author = f'book{book_id} author'
            )
            ctr+=1
