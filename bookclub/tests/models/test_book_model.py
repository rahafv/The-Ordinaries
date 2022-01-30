"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Book


class BookModelTestCase(TestCase):
    """Unit tests for the book model."""

    fixtures = ['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/default_book.json'
    ]
    
    def setUp(self):
        self.book = Book.objects.get(id=1)
    
    def test_valid_book(self):
        self._assert_book_is_valid()

    def test_ISBN_cannot_be_blank(self):
        self.book.ISBN = ''
        self._assert_book_is_invalid()

    def test_title_can_be_100_characters_long(self):
        self.book.title = 'x' * 100
        self._assert_book_is_valid()

    def test_title_cannot_be_over_100_characters_long(self):
        self.book.title = 'x' * 101
        self._assert_book_is_invalid()

    def test_author_can_be_100_characters_long(self):
        self.book.author = 'x' * 100
        self._assert_book_is_valid()

    def test_author_cannot_be_over_100_characters_long(self):
        self.book.author = 'x' * 101
        self._assert_book_is_invalid()

    def test_publisher_can_be_100_characters_long(self):
        self.book.publisher = 'x' * 100
        self._assert_book_is_valid()

    def test_publisher_cannot_be_over_100_characters_long(self):
        self.book.publisher = 'x' * 101
        self._assert_book_is_invalid()


    def test_ISBN_must_be_unique(self):
        self.create_second_book()
        second_book = Book.objects.get(ISBN='0002005018')
        self.book.ISBN = second_book.ISBN
        self._assert_book_is_invalid()


    def test_title_must_not_be_blank(self):
        self.book.title = ''
        self._assert_book_is_invalid()

    def test_author_must_not_be_blank(self):
        self.book.author = ''
        self._assert_book_is_invalid()  


    def test_title_need_not_be_unique(self):
        self.create_second_book()
        second_user = Book.objects.get(ISBN='0002005018')
        self.book.title = second_user.title
        self._assert_book_is_valid()

    def test_author_need_not_be_unique(self):
        self.create_second_book()
        second_user = Book.objects.get(ISBN='0002005018')
        self.book.author = second_user.author
        self._assert_book_is_valid()

    def test_publisher_need_not_be_unique(self):
        self.create_second_book()
        second_user = Book.objects.get(ISBN='0002005018')
        self.book.publisher = second_user.publisher
        self._assert_book_is_valid()

    def test_year_need_not_be_unique(self):
        self.create_second_book()
        second_user = Book.objects.get(ISBN='0002005018')
        self.book.year = second_user.year
        self._assert_book_is_valid()

    
    def test_year_may_be_blank(self):
        self.book.year = None
        self._assert_book_is_valid()

    def _assert_book_is_valid(self):
        try:
            self.book.full_clean()
        except (ValidationError):
            self.fail('Test book should be valid')

    def _assert_book_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.book.full_clean()

    def create_second_book(self):
        Book.objects.create(
            ISBN= "0002005018",
            title= "Clara Callan",
            author= "Richard Bruce Wright",
            publisher= "HarperFlamingo Canada",
            image_url= "http://images.amazon.com/images/P/0002005018.01.MZZZZZZZ.jpg",
            year= "2001"
        )

    def test_reader_addition(self):
        nonReader = User.objects.get(id=1)
        count = self.book.readers_count()
        self.book.add_reader(nonReader)
        self.assertEqual(self.book.readers_count(), count+1)

