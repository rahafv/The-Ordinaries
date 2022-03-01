# from datetime import datetime
# from django.test import TestCase
# from django.urls import reverse
# import pytz
# from bookclub.forms import MeetingForm
# from bookclub.models import Meeting, User, Club, Event
# from bookclub.tests.helpers import LoginRedirectTester , MenueTestMixin, MessageTester

# class ScheduleMeetingTest(TestCase, LoginRedirectTester, MenueTestMixin, MessageTester):

#     fixtures=['bookclub/tests/fixtures/default_user.json', 
#         'bookclub/tests/fixtures/other_users.json', 
#         'bookclub/tests/fixtures/default_club.json',
#         'bookclub/tests/fixtures/default_book.json',
#         'bookclub/tests/fixtures/default_meeting.json', 
#         'bookclub/tests/fixtures/other_meeting.json',]

#     def setUp(self):
#         self.club = Club.objects.get(id=1)
#         self.owner = User.objects.get(id=2)
#         self.url = reverse("schedule_meeting", kwargs={'club_id':self.club.id})

#         self.form_input = {
#             'title': 'meeting1',
#             'time': pytz.utc.localize(datetime.today()),
#             'notes': 'bring the book',
#             'link': 'https://goo.gl/maps/DbTzHjUu8cP4zNjRA'
#         }

#         self.sec_form_input = {
#             'title': 'meeting2',
#             'time': datetime.today(),
#             'notes': 'bring the book',
#             'link': 'https://goo.gl/maps/DbTzHjUu8cP4zNjRA',
#             'cont': True
#         }

#     def test_schedule_meeting_url(self):
#         self.assertEqual(self.url, f'/club/{self.club.id}/schedule_meeting/')

#     def test_schedule_meeting_get(self):
#         self.client.login(username=self.owner.username, password="Password123")
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "schedule_meeting.html")
#         form = response.context["form"]
#         self.assertTrue(isinstance(form, MeetingForm))
#         self.assertFalse(form.is_bound)
#         self.assert_menu(response)
 
#     def test_schedule_meeting_successful(self):
#         self.client.login(username=self.owner.username, password="Password123")
#         count_meetings_before = Meeting.objects.count()
#         count_events_before = Event.objects.count() 
#         response = self.client.post(self.url, self.form_input, follow=True)
#         self.assertEqual(count_meetings_before + 1, Meeting.objects.count())
#         self.assertEqual(count_events_before + 1, Event.objects.count())
#         target_url = reverse("club_page", kwargs={"club_id": self.club.id})
#         self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
#         self.assertTemplateUsed(response, "schedule_meeting.html")
#         # club = Club.objects.get(name="Club1")
#         # self.assertEqual(club.name, "Club1")
#         # self.assertEqual(club.theme, "Fiction")
#         # self.assertEqual(club.meeting_type, Club.MeetingType.INPERSON)
#         # self.assertEqual(club.club_type, Club.ClubType.PRIVATE)
#         # self.assertEqual(club.city, "nyc")
#         # self.assertEqual(club.country, "usa")
#         # owner = User.objects.get(username="johndoe")
#         # self.assertEqual(club.owner, owner)
#         # self.assert_menu(response)

#     # def test_schedule_meeting_unsuccessful(self):
#     #     self.client.login(username=self.owner.username, password="Password123")
#     #     count_meetings_before = Meeting.objects.count()
#     #     self.form_input["title"] = ""
#     #     response = self.client.post(self.url, self.form_input)
#     #     self.assertEqual(count_meetings_before, Meeting.objects.count())
#     #     self.assertEqual(response.status_code, 200)
#     #     form = response.context["form"]
#     #     self.assertTrue(form.is_bound)
#     #     self.assertTemplateUsed(response, "schedule_meeting.html")
#     #     self.assertTrue(isinstance(form, MeetingForm))
#     #     self.assert_menu(response)

#     def test_get_create_club_redirects_when_not_logged_in(self):
#         self.assert_redirects_when_not_logged_in()

#     def test_post_create_club_redirects_when_not_logged_in(self):
#         self.assert_post_redirects_when_not_logged_in()