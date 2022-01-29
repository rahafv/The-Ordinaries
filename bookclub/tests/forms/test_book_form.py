"""Unit tests of the club form."""
from django import forms
from django.test import TestCase
from bookclub.models import User, Book
from bookclub.forms import BookForm


class BookFormTestCase(TestCase):
    """Unit tests of the book form."""

    def setUp(self):
        self.form_input = {
            'ISBN': '0195153448',
            'title':'Classical',
            'author': 'Mark',
            'publisher': 'Oxford',
            'year': 2002,
        }
    
    def test_valid_add_book_form(self):
        form = BookForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = BookForm()
        self.assertIn('ISBN', form.fields)
        self.assertIn('title', form.fields)
        self.assertIn('author', form.fields)
        self.assertIn('publisher', form.fields)
        self.assertIn('year', form.fields)

    def test_club_form_must_save_correctly(self):
        form = BookForm(data=self.form_input)
        before_count = Book.objects.count() 
        form.save()
        after_count = Book.objects.count()
        self.assertEqual(after_count, before_count+1)
        book = Book.objects.get(ISBN = '0195153448')
        self.assertEqual(book.title, 'Classical')
        self.assertEqual(book.author, 'Mark')
        self.assertEqual(book.publisher, 'Oxford')
        self.assertEqual(book.year, 2002)
