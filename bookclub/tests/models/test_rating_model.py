"""Unit tests for the Rating model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Book , Rating 


class BookModelTestCase(TestCase):
    """Unit tests for the rating model."""

    fixtures = ['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/default_book.json'
    ]
    
    def setUp(self):
        self.book = Book.objects.get(id=1)

    