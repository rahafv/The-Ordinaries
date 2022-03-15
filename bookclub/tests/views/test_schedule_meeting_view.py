from datetime import datetime, timedelta
from django.test import RequestFactory, TestCase
from django.urls import reverse
from bookclub.forms import MeetingForm
from bookclub.helpers import MeetingHelper
from bookclub.models import Book, Meeting, User, Club, Event
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin, MessageTester
import pytz

class ScheduleMeetingTest(TestCase, LoginRedirectTester, MenuTestMixin, MessageTester):

    fixtures=['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_club.json', 
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/default_book.json',
        'bookclub/tests/fixtures/default_meeting.json',
        'bookclub/tests/fixtures/other_meeting.json']

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.owner = User.objects.get(id=2)
        self.sec_club = Club.objects.get(id=3)
        self.sec_owner = User.objects.get(id=3)
        self.user = User.objects.get(id=3)
        self.url = reverse("schedule_meeting", kwargs={'club_id':self.club.id})
        self.sec_url = reverse("schedule_meeting", kwargs={'club_id':self.sec_club.id})
        self.date = pytz.utc.localize(datetime.today()+timedelta(15))

        self.form_input = {
            'title': 'meeting1',
            'time': self.date,
            'notes': 'bring the book',
            'link': 'https://goo.gl/maps/DbTzHjUu8cP4zNjRA',
            'cont': False,
        }

        self.sec_form_input = {
            'title': 'meeting2',
            'time': self.date,
            'notes': 'bring the book',
            'link': 'https://goo.gl/maps/DbTzHjUu8cP4zNjRA',
            'cont': True
        }

    def test_schedule_meeting_url(self):
        self.assertEqual(self.url, f'/club/{self.club.id}/schedule_meeting/')

    def test_schedule_meeting_get(self):
        self.client.login(username=self.owner.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "schedule_meeting.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, MeetingForm))
        self.assertFalse(form.is_bound)
        self.assert_menu(response)
 
    def test_schedule_meeting_successful_when_cont(self):
        self.client.login(username=self.owner.username, password="Password123")
        count_meetings_before = Meeting.objects.count()
        count_events_before = Event.objects.count() 
        response = self.client.post(self.url, self.sec_form_input, follow=True)
        self.assertEqual(count_meetings_before + 1, Meeting.objects.count())
        self.assertEqual(count_events_before + 1, Event.objects.count())
        target_url = reverse("club_page", kwargs={"club_id": self.club.id})
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "club_page.html")
        meeting = Meeting.objects.get(title="meeting2")
        self.assertEqual(meeting.title, "meeting2")
        self.assertEqual(meeting.time, self.date)
        self.assertEqual(meeting.notes, "bring the book")
        self.assertEqual(meeting.link, "https://goo.gl/maps/DbTzHjUu8cP4zNjRA")
        self.assert_success_message(response)
        self.assert_menu(response)

    def test_schedule_meeting_unsuccessful(self):
        self.client.login(username=self.owner.username, password="Password123")
        count_meetings_before = Meeting.objects.count()
        self.form_input["title"] = ""
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(count_meetings_before, Meeting.objects.count())
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertTemplateUsed(response, "schedule_meeting.html")
        self.assertTrue(isinstance(form, MeetingForm))
        self.assert_menu(response)

    def test_only_owner_can_schedule(self):
        self.client.login(username=self.user.username, password="Password123")
        count_meetings_before = Meeting.objects.count()
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(count_meetings_before, Meeting.objects.count())

    def test_cant_schedule_with_no_members(self):
        self.client.login(username=self.sec_owner.username, password="Password123")
        count_meetings_before = Meeting.objects.count()
        response = self.client.get(self.sec_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(count_meetings_before, Meeting.objects.count())

    def test_send_email_to_chooser(self):
        meeting = Meeting.objects.get(id=1)
        self.assertNotEqual(meeting.chooser, None)
        request = RequestFactory().get(self.url)
        MeetingHelper().send_email(request=request, 
            meeting=meeting, 
            subject='email to chooser', 
            letter='emails/chooser_reminder.html', 
            all_mem=False 
        ) 

    def test_assign_book_when_not_book(self):
        meeting = Meeting.objects.get(id=3)
        self.assertEqual(meeting.book, None)
        request = RequestFactory().get(self.url)
        MeetingHelper().assign_rand_book(meeting, request)
        self.assertNotEqual(meeting.book, None)

    def test_assign_book_when_book(self):
        meeting = Meeting.objects.get(id=1)
        self.assertEqual(meeting.book, Book.objects.get(id=1))
        MeetingHelper().assign_rand_book(meeting)

    def test_get_schedule_meeting_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_post_schedule_meeting_redirects_when_not_logged_in(self):
        self.assert_post_redirects_when_not_logged_in()
