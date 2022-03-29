"""Unit tests of the rating form."""
from django.test import TestCase
from bookclub.models import User, Book, Rating
from bookclub.forms import RatingForm

class RatingFormTestCase(TestCase):
    """Unit tests of the review form."""

    fixtures=['bookclub/tests/fixtures/default_book.json',
            'bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.form_input = {
            'user': 1,
            'book':1,
            'review': 'Great book',
            'rating': 4.0,
        }
       
        self.empty_rating_form_input= {
            'user': 1,
            'book':1,
            'review': 'Great book',
            'rating':None ,
        }

    
    def test_valid_add_review_form(self):
        form = RatingForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = RatingForm()
        self.assertIn('review', form.fields)
        self.assertIn('rating', form.fields)

    def test_club_form_must_save_correctly(self):
        before_count = Rating.objects.count() 
        user = User.objects.get(id=1)
        book = Book.objects.get(id=1)
        form = RatingForm(book=book, user=user, data=self.form_input)
        rating = form.save()
        after_count = Rating.objects.count()
        self.assertEqual(after_count, before_count+1)
        self.assertEqual(rating.user, user)
        self.assertEqual(rating.book, book)
        self.assertEqual(rating.review, 'Great book')
        self.assertEqual(rating.rating, 4*2)
 
    def test_review_form_must_save_correctly_and_rating_can_be_empty(self):
        user = User.objects.get(id=1)
        book = Book.objects.get(id=1)
        form = RatingForm(book=book, user=user, data=self.empty_rating_form_input)
        form.save()
        self.assertTrue(form.is_valid())
        

    