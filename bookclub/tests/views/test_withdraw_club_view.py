"""Tests of the withdraw club view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club


class withdrawClubViewTestCase(TestCase):
    """Test suite for the withdraw club view."""

    fixtures = ['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.url = reverse("withdraw_club", kwargs={"club_id": self.club.id})
        self.owner = User.objects.get(username="janedoe")
        self.member = User.objects.get(username="petrapickles")
        self.user = User.objects.get(username="peterpickles")


    def test_club_page_url(self):
        self.assertEqual(self.url, f"/withdraw_club/{self.club.id}/")

    def test_owner_cannot_withdraw_club(self):
        self.client.login(username=self.owner.username, password="Password123")
        before_count = self.club.member_count()
        response = self.client.post(self.url)
        after_count = self.club.member_count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        

    def test_non_member_cannot_withdraw_club(self):
        self.client.login(username=self.user.username, password="Password123")
        before_count = self.club.member_count()
        response = self.client.post(self.url)
        after_count = self.club.member_count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_member_successful_withdraw_club(self):
        self.client.login(username=self.member.username, password="Password123")
        before_count = self.club.member_count()
        response = self.client.post(self.url)
        after_count = self.club.member_count()
        self.assertFalse(self.club.is_member(self.user))
        self.assertEqual(after_count, before_count - 1)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)


    def test_withdraw_club_with_invalid_id(self):
        self.client.login(username=self.member.username, password="Password123")
        url = reverse("withdraw_club", kwargs={"club_id": self.club.id + 9999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.club.is_member(self.user))

  
    def test_withdraw_club_redirects_when_not_logged_in(self):
        target_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "log_in.html")