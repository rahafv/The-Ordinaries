"""Tests of the transfer ownership user view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenuTestMixin

class TransferClubOwnershipTestCase(TestCase, MessageTester, MenuTestMixin, LoginRedirectTester):
    """Tests of the transfer ownership user view."""

    fixtures = [
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = User.objects.get(username="janedoe")
        self.member = User.objects.get(username="peterpickles")
        self.url = reverse("transfer_ownership", kwargs={"club_id": self.club.id})
        self.form_input = {
            'new_owner':{self.member.id},
            'confirm':'checked',
            'submit':'Save'
	    }

    def test_accept_applicant_url(self):
        self.assertEqual(self.url, f"/club/{self.club.id}/transfer_ownership/")
    
    def test_form(self):
        self.client.login(username=self.owner.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assert_menu(response)

    def test_successful_ownership_transfer(self):
        self.client.login(username=self.owner.username, password="Password123")
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_menu(response)

    def test_ownership_transfer_with_empty_club(self):
        self.client.login(username=self.owner.username, password="Password123")
        self.club.members.remove(self.member)
        response = self.client.get(self.url, follow=True)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertEqual(self.club.owner, self.owner)
        self.assert_menu(response)

    def test_ownership_transfer_with_invalid_input(self):
        self.client.login(username=self.owner.username, password="Password123")
        response = self.client.post(self.url,{'selected_member':'', 'defaultCheck':'checked'})
        self.assertTemplateUsed(response, 'club_templates/transfer_ownership.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.club.owner, self.owner)
        self.assert_menu(response)

    def test_ownership_transfer_by_a_member_not_owner(self):
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assert_error_message(response)
        self.assert_menu(response)

    def test_get_transfer_ownership_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()
    
    def test_post_transfer_ownership_redirects_when_not_logged_in(self):
       self.assert_post_redirects_when_not_logged_in()