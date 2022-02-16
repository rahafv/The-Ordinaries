"""Unit tests of the edit review form."""
from django.test import TestCase
from bookclub.models import User, Book, Rating
from bookclub.forms import EditRatingForm

class EditRatingFormTestCase(TestCase):
    """Unit tests of the edit review form."""

    fixtures=['bookclub/tests/fixtures/default_book.json',
            'bookclub/tests/fixtures/default_user.json' , 
            'bookclub/tests/fixtures/default_rating.json',]

    def setUp(self):
         self.review = Rating.objects.get(id = 1)
         self.form_input = {
            'user': 1,
            'book':1,
            'review': 'Great book',
            'rating': 4.0,
        }
         self.updated_form_input= {
            'user': 1,
            'book':1,
            'review': 'not so great book',
            'rating': None
        }


    def test_valid_Edit_review_form(self):
        form = EditRatingForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = EditRatingForm()
        self.assertIn('review', form.fields)
        self.assertIn('rating', form.fields)

    def test_form_uses_model_validation_rating(self):
        self.form_input['rating'] = 11
        form = EditRatingForm(data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_uses_model_validation_review(self):
        self.form_input['review'] = ""
        form = EditRatingForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_edit_review_form_must_save_correctly_but_no_new_object_created(self):
        form = EditRatingForm(data=self.form_input)
        before_count = Rating.objects.count() 
        user = User.objects.get(id=1)
        book = Book.objects.get(id=1)
        form.save(user, book)
        after_count = Rating.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(self.review.user, user)
        self.assertEqual(self.review.book, book)

    def test_edit_review_form_must_save_correctly_and_rating_can_be_empty(self):
        form = EditRatingForm(data=self.updated_form_input)
        user = User.objects.get(id=1)
        book = Book.objects.get(id=1)
        form.save(user, book)
        self.assertTrue(form.is_valid())

      

        

    