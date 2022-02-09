"""Tests of the show club view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester

class ShowClubViewTestCase(TestCase, LoginRedirectTester):
    """Test suite for the show club view."""

    fixtures = ['bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/other_club.json', 
        'bookclub/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.url = reverse("club_page", kwargs={"club_id": self.club.id})
        self.owner = User.objects.get(username="janedoe")

    def test_club_page_url(self):
        self.assertEqual(self.url, f"/club/{self.club.id}/")

    def test_get_club_page_with_valid_id(self):
        self.client.login(username=self.owner.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_page.html")

    def test_get_club_page_with_invalid_id(self):
        self.client.login(username=self.owner.username, password="Password123")
        url = reverse("club_page", kwargs={"club_id": self.club.id + 99999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_get_club_page_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()