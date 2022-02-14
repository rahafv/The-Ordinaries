"""Tests for the edit view view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import EditRatingForm
from bookclub.models import User, Club , Rating
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenueTestMixin

class ReviewUpdateViewTest(TestCase, LoginRedirectTester, MessageTester,MenueTestMixin):
    """Test suite for the edit review view."""

    fixtures = [
        'bookclub/tests/fixtures/default_rating.json',
        # 'bookclub/tests/fixtures/other_ratings.json',
        'bookclub/tests/fixtures/default_user.json' , 
        'bookclub/tests/fixtures/default_book.json'
    ]

    def setUp(self):
        self.rating = Rating.objects.get(id=1)
        self.url = reverse("edit_review", kwargs={"review_id": self.rating.id})
        self.form_input = {
            'user': 1,
            'book':1,
            'review': 'Great book',
            'rating': 4.0,
        }
     
    def test_edit_review_url(self):
        self.assertEqual(self.url, f"/edit_review/{self.rating.id}")

 
    def test_get_edit_review(self):
        self.client.login(username=self.rating.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_review.html')
        review_id = response.context['review_id']
        form= response.context['form']
        self.assertTrue(isinstance(form, EditRatingForm)) 
        self.assertEqual(form.instance, self.rating)
        self.assertEqual(review_id, self.rating.id)
        self.assert_menu(response)

    def test_unsuccessful_review_update(self):
        self.client.login(username=self.rating.user.username, password="Password123")
        count_clubs_before = Rating.objects.count()
        self.form_input["review"] = "x"*255
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(count_clubs_before, Rating.objects.count())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_review.html")


    def test_successful_review_update(self):
        self.client.login(username=self.rating.user.username, password="Password123")
        count_ratings_before = Rating.objects.count()
        target_url = reverse("book_details", kwargs={"book_id": 1})
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "book_details.html")
        self.assertEqual(count_ratings_before, Club.objects.count()+1)
        self.assert_success_message(response)
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.user.id, 1)
        self.assertEqual(self.rating.book.id, 1)
        self.assertEqual(self.rating.review, 'Great book')
        self.assertEqual(self.rating.rating, 4.0*2)
        self.assert_menu(response)

    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()
    
    def test_post_profile_redirects_when_not_logged_in(self):
       self.assert_post_redirects_when_not_logged_in()