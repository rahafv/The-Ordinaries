"""Tests of the join club view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenuTestMixin

class JoinClubViewTestCase(TestCase, LoginRedirectTester, MessageTester,MenuTestMixin):
    """Test suite for the join club view."""

    fixtures = [
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/default_club.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.url = reverse("join_club", kwargs={"club_id": self.club.id})
        self.owner = User.objects.get(username="janedoe")
        self.member = User.objects.get(username="peterpickles")
        self.user = User.objects.get(username="edgaralen")
        self.applicant = User.objects.get(username = "willsmith")
        self.follower = User.objects.get(username = "willsmith")
        self.follower.toggle_follow(self.user)

    def test_join_url(self):
        self.assertEqual(self.url, f"/club/{self.club.id}/join/")

    def test_owner_cannot_join_club(self):
        self.client.login(username=self.owner.username, password="Password123")
        before_count = self.club.member_count()
        response = self.client.get(self.url, follow=True)
        after_count = self.club.member_count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_error_message(response)
        self.assert_menu(response)
        
    def test_member_cannot_join_club(self):
        self.client.login(username=self.member.username, password="Password123")
        before_count = self.club.member_count()
        response = self.client.get(self.url, follow=True)
        after_count = self.club.member_count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_error_message(response)
        self.assert_menu(response)

    def test_non_member_successful_join_club(self):
        self.client.login(username=self.user.username, password="Password123")
        members_before_count = self.club.member_count()
        events_before_count =  self.follower.notifications.unread().count()
        response = self.client.get(self.url, follow=True)
        self.assertTrue(self.club.is_member(self.user))
        self.assertEqual(members_before_count + 1, self.club.member_count())
        self.assertEqual(events_before_count + 1, self.follower.notifications.unread().count())
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
        self.assert_menu(response)

    def test_user_cannot_join_private_club_before_approval(self):
        self.club.club_type = Club.ClubType.PRIVATE
        self.club.save()
        self.client.login(username=self.user.username, password="Password123")
        before_count = self.club.member_count()
        applicants_before_count = self.club.applicants_count()
        response = self.client.get(self.url, follow=True)
        after_count = self.club.member_count()
        applicants_after_count = self.club.applicants_count()
        self.assertFalse(self.club.is_member(self.user))
        self.assertTrue(self.club.is_applicant(self.user))
        self.assertEqual(after_count, before_count)
        self.assertEqual(applicants_after_count, applicants_before_count + 1)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
        self.assert_menu(response)
    
    def test_applicant_cannot_re_apply_for_private_clubs(self):
        self.club.club_type = Club.ClubType.PRIVATE
        self.club.save()
        self.club.add_applicant(self.applicant)
        self.client.login(username=self.applicant.username, password="Password123")
        before_count = self.club.member_count()
        applicants_before_count = self.club.applicants_count()
        response = self.client.get(self.url, follow=True)
        after_count = self.club.member_count()
        applicants_after_count = self.club.applicants_count()
        self.assertFalse(self.club.is_member(self.applicant))
        self.assertTrue(self.club.is_applicant(self.applicant))
        self.assertEqual(after_count, before_count)
        self.assertEqual(applicants_after_count, applicants_before_count)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_info_message(response)
        self.assert_menu(response)

    def test_join_club_with_invalid_id(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse("join_club", kwargs={"club_id": self.club.id + 9999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.club.is_member(self.user))

    def test_join_club_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()