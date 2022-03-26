"""Tests of the sign up view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Book, Rating, User
from bookclub.tests.helpers import LoginRedirectTester

class AddReviewViewTestCase(TestCase, LoginRedirectTester):
    """Tests of the add bookview."""

    fixtures = ["bookclub/tests/fixtures/default_book.json", 
                'bookclub/tests/fixtures/default_user.json', 
                'bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.book = Book.objects.get(ISBN='0195153448')
        self.url = reverse("add_review",  kwargs={"book_id": self.book.id})
        self.user = User.objects.get(id=1)
        self.form_input = {
            'user': 1,
            'book':1,
            'review': 'Great book',
            'rating': 4.0,
        }
        self.follower =  User.objects.get(id=2)
        self.follower.toggle_follow(self.user)
        self.user.toggle_follow(self.follower)

    def test_add_review_url(self):
        self.assertEqual(self.url,f"/book/{self.book.id}/add_review")

    def test_get_rating_form(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')

    def test_user_cannot_rate_twice(self):
        self.client.login(username=self.user.username, password="Password123")
        target_url = reverse("book_details",  kwargs={"book_id": self.book.id})
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        count_rating_before = Rating.objects.count()
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(count_rating_before, Rating.objects.count())

    def test_add_review_successful(self):
        self.client.login(username=self.user.username, password="Password123")
        count_rating_before = Rating.objects.count()
        count_events_before = self.follower.notifications.unread().count()
        target_url = reverse("book_details",  kwargs={"book_id": self.book.id})
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "book_details.html")
        self.assertEqual(count_rating_before + 1, self.follower.notifications.unread().count())
        self.assertEqual(count_events_before + 1, self.follower.notifications.unread().count())
        user = User.objects.get(id=1)
        book = Book.objects.get(id=1)
        rating = Rating.objects.get(user=user.id, book=book.id)
        self.assertEqual(rating.user, user)
        self.assertEqual(rating.book, book)
        self.assertEqual(rating.review, 'Great book')
        self.assertEqual(rating.rating, 4*2)

    def test_add_review_unsuccessful(self):
        self.client.login(username=self.user.username, password="Password123")
        count_clubs_before = Rating.objects.count()
        self.form_input["review"] = "x"*251
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(count_clubs_before, Rating.objects.count())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "book_details.html")

    def test_get_add_book_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_post_add_book_redirects_when_not_logged_in(self):
        self.assert_post_redirects_when_not_logged_in()


