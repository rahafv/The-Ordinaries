"""Tests of the join club view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Event
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenuTestMixin

class AcceptApplicantViewTestCase(TestCase, LoginRedirectTester, MessageTester,MenuTestMixin):
    """Test suite for the join club view."""

    fixtures = [
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = User.objects.get(username="janedoe")
        self.member = User.objects.get(username="peterpickles")
        self.user = User.objects.get(username="edgaralen")
        self.url = reverse("accept_applicant", kwargs={"club_id": self.club.id, "user_id":self.user.id })
        self.club.add_applicant(self.user)



    def test_accept_applicant_url(self):
        self.assertEqual(self.url, f"/club/{self.club.id}/applicants/accept/{self.user.id}")

    def test_member_cannot_accept_user(self):
        self.client.login(username=self.member.username, password="Password123")
        before_count = self.club.member_count()
        applicants_before_count = self.club.applicants_count()
        response = self.client.get(self.url, follow=True)
        after_count = self.club.member_count()
        applicants_after_count = self.club.applicants_count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(applicants_after_count, applicants_before_count)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_error_message(response)
        self.assert_menu(response)
        

    def test_user_cannot_accept_user(self):
        self.client.login(username=self.user.username, password="Password123")
        before_count = self.club.member_count()
        applicants_before_count = self.club.applicants_count()
        response = self.client.get(self.url, follow=True)
        after_count = self.club.member_count()
        applicants_after_count = self.club.applicants_count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(applicants_after_count, applicants_before_count)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_error_message(response)
        self.assert_menu(response)

    def test_non_member_successful_acceptance_in_club(self):
        self.client.login(username=self.owner.username, password="Password123")
        before_count = self.club.member_count()
        # events_before_count = self.owner.notifications.unread().count
        self.assertTrue(self.club.is_applicant(self.user))
        applicants_before_count = self.club.applicants_count()
        response = self.client.get(self.url, follow=True)
        after_count = self.club.member_count()
        applicants_after_count = self.club.applicants_count()
        self.assertTrue(self.club.is_member(self.user))
        self.assertFalse(self.club.is_applicant(self.user))
        self.assertEqual(after_count, before_count + 1)
        # self.assertEqual(events_before_count + 1,self.owner.notifications.unread().count)
        self.assertEqual(applicants_after_count, applicants_before_count - 1)
        response_url = reverse('applicants_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
        self.assert_menu(response)

    def test_accept_applicant_with_invalid_id(self):
        self.client.login(username=self.owner.username, password="Password123")
        url = reverse("accept_applicant", kwargs={"club_id": self.club.id, "user_id": self.user.id + 9999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.club.is_member(self.user))

  
    def test_accept_applicant_view_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()