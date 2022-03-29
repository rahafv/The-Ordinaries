"""Tests of the withdraw club view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenuTestMixin



class withdrawClubViewTestCase(TestCase, LoginRedirectTester, MessageTester,MenuTestMixin):
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
        self.member = User.objects.get(username="peterpickles")
        self.user = User.objects.get(username="edgaralen")
        self.follower = User.objects.get(username="willsmith")
        self.follower.toggle_follow(self.user)
        self.follower.toggle_follow(self.member)
        

    def test_withdarw_url(self):
        self.assertEqual(self.url, f"/club/{self.club.id}/withdraw_club")

    def test_owner_cannot_withdraw_club(self):
        self.client.login(username=self.owner.username, password="Password123")
        before_count = self.club.member_count()
        response = self.client.get(self.url, follow=True)
        after_count = self.club.member_count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_error_message(response)
        self.assert_menu(response)
        
    def test_non_member_cannot_withdraw_club(self):
        self.client.login(username=self.user.username, password="Password123")
        before_count = self.club.member_count()
        response = self.client.get(self.url, follow=True)
        after_count = self.club.member_count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_error_message(response)
        self.assert_menu(response)

    def test_member_successful_withdraw_club(self):
        self.client.login(username=self.member.username, password="Password123")
        before_count = self.club.member_count()
        events_before_count = self.follower.notifications.unread().count()
        response = self.client.get(self.url, follow=True)
        self.assertFalse(self.club.is_member(self.user))
        self.assertEqual(before_count - 1, self.club.member_count())
        self.assertEqual(events_before_count + 1,self.follower.notifications.unread().count())
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
        self.assert_menu(response)

    def test_user_joins_then_withdraws_deletes_join_event(self):
        self.client.login(username=self.user.username, password="Password123")
        join_url = reverse("join_club", kwargs={"club_id": self.club.id})
        response = self.client.get(join_url, follow=True)
        events_after_joining_count =self.follower.notifications.unread().count()
        response = self.client.get(self.url, follow=True)
        response = self.client.get(join_url, follow=True)
        events_after_withdrawing_count = self.follower.notifications.unread().count()
        self.assertEqual(events_after_joining_count, 1)
        self.assertEqual(events_after_withdrawing_count, 2)
  

    def test_withdraw_club_with_invalid_id(self):
        self.client.login(username=self.member.username, password="Password123")
        url = reverse("withdraw_club", kwargs={"club_id": self.club.id + 9999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.club.is_member(self.user))

  
    def test_withdraw_club_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()