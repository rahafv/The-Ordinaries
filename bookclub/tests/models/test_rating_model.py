"""Unit tests for the Rating model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Book , Rating 


class RatingModelTestCase(TestCase):
    """Unit tests for the rating model."""

    fixtures = ['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/default_book.json' , 
        'bookclub/tests/fixtures/default_rating.json' , 
        'bookclub/tests/fixtures/other_ratings.json' , 
        'bookclub/tests/fixtures/other_users.json' , 
        'bookclub/tests/fixtures/other_books.json'    
    ]
    
    def setUp(self):
        self.rating = Rating.objects.get(id=1)
        self.other_rating = Rating.objects.get(id=2)

    def test_review_cannot_be_over_250_characters_long(self):
        self.rating.review = 'x' * 251
        self._assert_rating_is_invalid()
    
    def test_review_can_be_250_characters_long(self):
        self.rating.review = 'x' * 250
        self._assert_rating_is_valid()

    def test_rating_created(self):
        self.assertEqual(2, Rating.objects.count())

    def test_rating_cannot_be_blank(self):
        self.rating.rating = ''
        self._assert_rating_is_invalid() 
    
    def test_review_may_be_blank(self):
        self.rating.review = None
        self._assert_rating_is_valid()

    def test_rating_cannot_be_over_five(self):
        self.rating.rating = 6
        self._assert_rating_is_invalid() 

    def test_rating_cannot_be_less_than_one(self):
        self.rating.rating = 0
        self._assert_rating_is_invalid() 


    def _assert_rating_is_valid(self):
        try:
            self.rating.full_clean()
        except (ValidationError):
            self.fail('Test rating should be valid')

    def _assert_rating_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.rating.full_clean()
            
       

    