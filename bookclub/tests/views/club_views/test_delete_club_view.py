"""Tests of the delete club view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester, MessageTester 

class DeleteClubViewTestCase(TestCase, LoginRedirectTester, MessageTester):
    """Tests of the delete club view."""
    
    fixtures = ['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.url = reverse("delete_club", kwargs={"club_id": self.club.id})
        self.owner = User.objects.get(username="janedoe")
        self.member = User.objects.get(username="peterpickles")

    def test_delete_club_url(self):
        self.assertEqual(self.url, f"/club/{self.club.id}/delete/")

    def test_member_cannot_delete_club(self):
        self.client.login(username=self.member.username, password="Password123")
        before_count = Club.objects.count() 
        response = self.client.get(self.url, follow=True)
        self.assertEqual(before_count, Club.objects.count())
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_error_message(response)

    def test_owner_successful_delete_club(self):
        self.client.login(username=self.owner.username, password="Password123")
        before_count = Club.objects.count() 
        response = self.client.get(self.url, follow=True)
        self.assertEqual(before_count - 1, Club.objects.count() )
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
     
    def test_delete_club_with_invalid_id(self):
        self.client.login(username=self.owner.username, password="Password123")
        url = reverse("delete_club", kwargs={"club_id": self.club.id + 9999})
        before_count = Club.objects.count() 
        response = self.client.get(url, follow=True)
        self.assertEqual(before_count, Club.objects.count())
        self.assertEqual(response.status_code, 404)

    def test_delete_club_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()