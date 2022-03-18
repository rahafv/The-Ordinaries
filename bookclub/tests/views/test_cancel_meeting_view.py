"""Tests of the delete meeting view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Meeting
from bookclub.tests.helpers import LoginRedirectTester, MessageTester 

class withdrawClubViewTestCase(TestCase, LoginRedirectTester, MessageTester):
    fixtures = ['bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_meeting.json',
        'bookclub/tests/fixtures/other_meeting.json',
        'bookclub/tests/fixtures/default_book.json',
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.meeting = Meeting.objects.get(id=1)
        self.other_meeting = Meeting.objects.get(id=2)
        self.url = reverse("cancel_meeting", kwargs={"meeting_id": self.meeting.id})
        self.owner = User.objects.get(username="janedoe")
        self.member = User.objects.get(username="peterpickles")

    def test_cancel_meeting_url(self):
        self.assertEqual(self.url, f"/cancel_meeting/{self.meeting.id}")

    def test_member_cannot_cancel_meeting(self):
        self.client.login(username=self.member.username, password="Password123")
        before_count = Meeting.objects.count() 
        response = self.client.get(self.url, follow=True)
        self.assertEqual(before_count, Meeting.objects.count())
        response_url = reverse('meetings_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_error_message(response)

    def test_owner_successful_cancel_meeting(self):
        self.client.login(username=self.owner.username, password="Password123")
        before_count = Meeting.objects.count() 
        response = self.client.get(self.url, follow=True)
        self.assertEqual(before_count - 1, Meeting.objects.count() )
        response_url = reverse('meetings_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
     
    def test_cancel_meeting_with_invalid_id(self):
        self.client.login(username=self.owner.username, password="Password123")
        url = reverse("cancel_meeting", kwargs={"meeting_id": self.meeting.id + 9999})
        before_count = Meeting.objects.count() 
        response = self.client.get(url, follow=True)
        self.assertEqual(before_count, Meeting.objects.count())
        self.assertEqual(response.status_code, 404)

    def test_cancel_meeting_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()