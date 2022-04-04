"""Tests for the edit view view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import EditRatingForm
from bookclub.models import Rating
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenuTestMixin

class ReviewUpdateViewTest(TestCase, LoginRedirectTester, MessageTester,MenuTestMixin):
    """Test suite for the edit review view."""

    fixtures = [
        'bookclub/tests/fixtures/default_rating.json',
        'bookclub/tests/fixtures/default_user.json' , 
        'bookclub/tests/fixtures/default_book.json', 
        'bookclub/tests/fixtures/other_users.json' ,
        'bookclub/tests/fixtures/other_ratings.json' , 
        'bookclub/tests/fixtures/other_books.json'
    ]

    def setUp(self):
        self.rating = Rating.objects.get(id=1)
        self.other_rating = Rating.objects.get(id=2)
        self.url = reverse("edit_review", kwargs={"review_id": self.rating.id})
        self.other_url = reverse("edit_review", kwargs={"review_id": self.other_rating.id})
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
        self.assertTemplateUsed(response, 'book_templates/edit_review.html')
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
        self.assertTemplateUsed(response, "book_templates/edit_review.html")
        self.assert_error_message(response)

    def test_successful_review_update(self):
        self.client.login(username=self.rating.user.username, password="Password123")
        count_ratings_before = Rating.objects.count()
        target_url = reverse("book_details", kwargs={"book_id": 1})
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "book_templates/book_details.html")
        self.assertEqual(count_ratings_before, Rating.objects.count())
        self.assert_success_message(response)
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.user.id, 1)
        self.assertEqual(self.rating.book.id, 1)
        self.assertEqual(self.rating.review, 'Great book')
        self.assertEqual(self.rating.rating, 4.0*2)
        self.assert_menu(response)
    
    def test_user_cannot_access_edit_review_of_other_users(self):
        logged_in_user = self.client.login(username=self.rating.user.username, password="Password123")
        self.assertNotEquals(logged_in_user , self.other_rating.user.username)
        response = self.client.get(self.other_url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'static_templates/404_page.html')

    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()
    
    def test_post_profile_redirects_when_not_logged_in(self):
       self.assert_post_redirects_when_not_logged_in()