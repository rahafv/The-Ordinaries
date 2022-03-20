from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
import pytz
from bookclub.models import User, Club, Meeting, Book
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin
from system import settings

class MeetingsListTest(TestCase, LoginRedirectTester ,MenuTestMixin ):

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
        self.url = reverse('meetings_list', kwargs={'club_id': self.club.id})
        
    def test_meetings_list_url(self):
        self.assertEqual(self.url,f'/club/{self.club.id}/meetings/')

    def test_get_meetings_list_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()

    def test_get_club_meetings_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('meetings_list', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings_list.html')
        self.assert_menu(response)
        
    def test_get_meetings_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_meetings(12)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings_list.html')
        self.assertEqual(len(response.context['meetings_list']), 14)
        for meeting_id in range(11):
            self.assertContains(response, f'meeting {meeting_id}')
            self.assertContains(response, "https://us04web.zoom.us/j/74028123722?pwd=af96piEWRe9_XWlB1XnAjw4XDp4uk7.1")
        self.assert_menu(response)


    def test_get_members_list_with_pagination(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_meetings(settings.MEMBERS_PER_PAGE*2)
        response = self.client.get(self.url)
        self.assert_menu(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings_list.html')
        self.assertEqual(len(response.context['meetings_list']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['meetings_list']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('meetings_list', kwargs={'club_id': self.club.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings_list.html')
        self.assertEqual(len(response.context['meetings_list']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['meetings_list']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('meetings_list', kwargs={'club_id': self.club.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings_list.html')
        self.assertEqual(len(response.context['meetings_list']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['meetings_list']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('meetings_list', kwargs={'club_id': self.club.id}) + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings_list.html')
        self.assertEqual(len(response.context['meetings_list']), 2)
        page_obj = response.context['meetings_list']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
        self.assert_menu(response)


    def _create_test_meetings(self, meetings_count=10):
        time = datetime.today()
        for meeting_id in range(meetings_count):
            time = time + timedelta(32)
            Meeting.objects.create(title = f'meeting {meeting_id}',
                club = self.club,
                time = pytz.utc.localize(time),
                notes =f'notes of meeting {meeting_id}',
                link ="https://us04web.zoom.us/j/74028123722?pwd=af96piEWRe9_XWlB1XnAjw4XDp4uk7.1",
            )