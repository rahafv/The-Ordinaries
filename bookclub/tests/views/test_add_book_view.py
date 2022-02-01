"""Tests of the sign up view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import BookForm
from bookclub.models import Book
from bookclub.tests.helpers import LoginRedirectTester

class AddBookViewTestCase(TestCase, LoginRedirectTester):
    """Tests of the add bookview."""

    fixtures = ["bookclub/tests/fixtures/default_user.json"]

    def setUp(self):
        self.url =reverse('add_book')
        self.form_input = {
            'ISBN': '0195153448',
            'title':'Classical',
            'author': 'Mark',
            'publisher': 'Oxford',
            'year': 2002,
        }

    def test_add_book_url(self):
        self.assertEqual(self.url,'/add_book/')

    def test_get_add_book(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_book.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_book_addition(self):
        self.client.login(username="johndoe", password="Password123")
        self.form_input['ISBN'] = '1234567890'
        before_count = Book.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Book.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_book.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookForm))
        self.assertTrue(form.is_bound)

    def test_add_book_successful(self):
        self.client.login(username="johndoe", password="Password123")
        count_books_before = Book.objects.count()
        target_url = reverse("book_details", kwargs={"book_id": 1})
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "book_details.html")
        self.assertEqual(count_books_before + 1, Book.objects.count())
        club = Book.objects.get(ISBN="0195153448")
        self.assertEqual(club.title, "Classical")
        self.assertEqual(club.author, "Mark")
        self.assertEqual(club.publisher, "Oxford")
        self.assertEqual(club.year, 2002)

    def test_get_add_book_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_post_add_book_redirects_when_not_logged_in(self):
        self.assert_post_redirects_when_not_logged_in()
