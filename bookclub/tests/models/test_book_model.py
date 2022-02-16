"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Book, Club, Rating


class BookModelTestCase(TestCase):
    """Unit tests for the book model."""

    fixtures = ['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_book.json', 
        'bookclub/tests/fixtures/other_books.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_ratings.json'
    ]
    
    def setUp(self):
        self.book = Book.objects.get(id=1)
    
    def test_valid_book(self):
        self._assert_book_is_valid()

    def test_ISBN_cannot_be_blank(self):
        self.book.ISBN = ''
        self._assert_book_is_invalid()

    def test_title_can_be_200_characters_long(self):
        self.book.title = 'x' * 200
        self._assert_book_is_valid()

    def test_title_cannot_be_over_200_characters_long(self):
        self.book.title = 'x' * 201
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
        second_book = Book.objects.get(ISBN='0002005018')
        self.book.title = second_book.title
        self._assert_book_is_valid()

    def test_author_need_not_be_unique(self):
        second_book = Book.objects.get(ISBN='0002005018')
        self.book.author = second_book.author
        self._assert_book_is_valid()

    def test_publisher_need_not_be_unique(self):
        second_book = Book.objects.get(ISBN='0002005018')
        self.book.publisher = second_book.publisher
        self._assert_book_is_valid()

    def test_year_need_not_be_unique(self):
        second_book = Book.objects.get(ISBN='0002005018')
        self.book.year = second_book.year
        self._assert_book_is_valid()

    def test_year_may_be_blank(self):
        self.book.year = None
        self._assert_book_is_valid()

    def test_reader_addition(self):
        nonReader = User.objects.get(id=1)
        count = self.book.readers_count()
        self.book.add_reader(nonReader)
        self.assertEqual(self.book.readers_count(), count+1)

    def test_reader_deletion(self):
        nonReader = User.objects.get(id=1)
        self.book.add_reader(nonReader)
        count = self.book.readers_count()
        self.book.remove_reader(nonReader)
        self.assertEqual(self.book.readers_count(), count-1)

    def test_club_addition(self):
        club = Club.objects.get(id=1)
        count = self.book.clubs_count()
        self.book.add_club(club)
        self.assertEqual(self.book.clubs_count(), count+1)

    def test_average_rating(self):
        book = Book.objects.get(id=2)
        rating1 = Rating.objects.get(id=2).rating
        rating2 = Rating.objects.get(id=2).rating
        self.assertEqual(book.average_rating(), ((rating1+rating2)/2))

    def _assert_book_is_valid(self):
        try:
            self.book.full_clean()
        except (ValidationError):
            self.fail('Test book should be valid')

    def _assert_book_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.book.full_clean()



