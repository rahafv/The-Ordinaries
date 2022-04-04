"""Tests of the book list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Book
from bookclub.forms import BooksSortForm
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin, ObjectsCreator
from system import settings

class BooksListTest(TestCase, LoginRedirectTester, MenuTestMixin, ObjectsCreator):
    """Tests of the book list view."""

    fixtures=['bookclub/tests/fixtures/default_book.json',
                'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.target_book = Book.objects.get(ISBN='0195153448')
        self.user = User.objects.get(id=1)
        self.club = Club.objects.get(id=1)
        self.url = reverse('books_list')
        self.BOOKS_PER_PAGE = 15
        self.form_input = {
            'sort':BooksSortForm.DESC_NAME,
        }

    def test_books_list_url(self):
        self.assertEqual(self.url,f'/books/')

    def test_get_club_books_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('books_list', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')  
        self.assert_menu(response)


    def test_get_books_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.create_test_books(self.BOOKS_PER_PAGE-1)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        self.assertEqual(len(response.context['books']),self.BOOKS_PER_PAGE)
        for book_id in range(self.BOOKS_PER_PAGE-1):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
            books_url = reverse('books_list')
            self.assertContains(response, books_url)
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')  
        self.assert_menu(response)

    def test_get_user_empty_books_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.create_test_books(self.BOOKS_PER_PAGE-1)
        self.url = reverse('books_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        self.assertContains(response, f'The book list is empty! find more book you might like.')
        self.assertContains(response, f'More books')
        books_url = reverse('books_list')
        self.assertContains(response, books_url)
        self.assert_menu(response)

    def test_get_user_filled_books_list_asc_title(self):
        self.form_input['sort'] = BooksSortForm.ASC_NAME
        self.client.login(username=self.user.username, password='Password123')
        self.create_test_books(self.BOOKS_PER_PAGE-1)
        Book.objects.get(id=2).add_reader(self.user)
        Book.objects.get(id=3).add_reader(self.user)
        self.url = reverse('books_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        for book_id in range(2):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_asc')  
        self.assert_menu(response)


    def test_get_user_filled_books_list_desc_title(self):
        self.form_input['sort'] = BooksSortForm.DESC_NAME
        self.client.login(username=self.user.username, password='Password123')
        self.create_test_books(self.BOOKS_PER_PAGE-1)
        Book.objects.get(id=2).add_reader(self.user)
        Book.objects.get(id=3).add_reader(self.user)
        self.url = reverse('books_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        for book_id in range(2):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')  
        self.assert_menu(response)