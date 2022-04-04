"""Test suite for the meeting list view."""
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
import pytz
from bookclub.models import User, Club, Meeting, Book
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin, MessageTester 

class MeetingsListTest(TestCase, LoginRedirectTester ,MenuTestMixin, MessageTester ):
    """Test suite for the meeting list view."""

    fixtures=[
                'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_club.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/default_meeting.json',
                'bookclub/tests/fixtures/other_meeting.json',
                'bookclub/tests/fixtures/default_book.json', ]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.club = Club.objects.get(id=1)
        self.other_club = Club.objects.get(id=2)
        self.meeting = Meeting.objects.get(id=1)
        self.sec_meeting = Meeting.objects.get(id=4)
        self.book = Book.objects.get(id=1)
        self.url = reverse('previous_meetings_list', kwargs={'club_id': self.club.id})
        
    def test_previous_meetings_list_url(self):
        self.assertEqual(self.url,f'/club/1/previous_meetings/')

    def test_get_previous_meetings_list_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()

    def test_get_club_previous_meetings_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.club.add_member(self.user)
        self.url = reverse('previous_meetings_list', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_templates/meetings_list.html')
        self.assert_menu(response)
        
    def test_get_previous_meetings_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.club.add_member(self.user)
        self._create_test_previous_meetings()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meeting_templates/meetings_list.html')
        self.assertEqual(len(response.context['meetings_list']),14)
        for meeting_id in range(10):
            self.assertContains(response, f'meeting {meeting_id}')
            self.assertContains(response, "https://us04web.zoom.us/j/74028123722?pwd=af96piEWRe9_XWlB1XnAjw4XDp4uk7.1")
        self.assert_menu(response)

    def test_non_members_cannot_access_previous_meetings_list(self):
        self.non_member = User.objects.get(id=4)
        self.client.login(username=self.non_member.username, password='Password123')
        self._create_test_previous_meetings()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_templates/club_page.html")
        self.assert_error_message(response)
        self.assert_menu(response)

    def _create_test_previous_meetings(self, meetings_count=10):
        time = datetime.today() - timedelta(350)
        for meeting_id in range(meetings_count):
            time = time + timedelta(32)
            Meeting.objects.create(title = f'meeting {meeting_id}',
                club = self.club,
                time = pytz.utc.localize(time),
                notes =f'notes of meeting {meeting_id}',
                link ="https://us04web.zoom.us/j/74028123722?pwd=af96piEWRe9_XWlB1XnAjw4XDp4uk7.1",
            )
            