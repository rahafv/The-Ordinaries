"""Unit tests for the Rating model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from bookclub.models import User, Book , Rating 


class RatingModelTestCase(TestCase):
    """Unit tests for the rating model."""

    fixtures = ['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/default_book.json'
    ]
    
    def setUp(self):
            self.rating = Rating.objects.create(
                user = User.objects.get(id=1) , 
                book = Book.objects.get(id=1),
                review = 'this book is very nice!' , 
                rating = 3,
            )

    def test_review_cannot_be_over_250_characters_long(self):
        self.rating.review = 'x' * 251
        self._assert_rating_is_invalid()
    
    def test_review_can_be_250_characters_long(self):
        self.rating.review = 'x' * 250
        self._assert_rating_is_valid()

    def test_rating_created(self):
        self.assertEqual(1, Rating.objects.count())

    


    def _assert_rating_is_valid(self):
        try:
            self.rating.full_clean()
        except (ValidationError):
            self.fail('Test rating should be valid')

    def _assert_rating_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.rating.full_clean()
            
       

    