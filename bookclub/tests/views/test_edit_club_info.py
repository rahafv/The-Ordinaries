"""Tests for the profile view."""
from django.test import TestCase
from django.urls import reverse
#from bookclub.forms import ClubForm
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenuTestMixin

class ClubUpdateViewTest(TestCase, LoginRedirectTester, MessageTester,MenuTestMixin):
    """Test suite for the profile view."""

    fixtures = [
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(id=1)
        self.url = reverse("edit_club", kwargs={"club_id": self.club.id})
        self.owner = User.objects.get(username="janedoe")
        self.form_input = {
            'name': 'club2.0',
            'theme':'Drama',
            'meeting_type':Club.MeetingType.INPERSON,
            'club_type': Club.ClubType.PRIVATE,
            'city' : 'New York',
            'country' : 'USA',
        }

    def test_edit_club_page_url(self):
        self.assertEqual(self.url, f"/club/{self.club.id}/edit_club/")


    def test_get_edit_club(self):
        self.client.login(username=self.owner.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club_info.html')
        club_id = response.context['club_id']
        form= response.context['form']
        #self.assertTrue(isinstance(form, ClubForm)) 
        self.assertEqual(form.instance, self.club)
        self.assertEqual(club_id, self.club.id)
        self.assert_menu(response)


    def test_unsuccessful_club_info_update(self):
        self.client.login(username=self.owner.username, password='Password123')
        self.form_input['name'] = ''
        before_count = Club.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Club.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_club_info.html')
        form = response.context['form']
        #self.assertTrue(isinstance(form, ClubForm))
        self.assertTrue(form.instance, self.club)
        self.assertTrue(form.is_bound)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, 'club1')
        self.assertEqual(self.club.theme, 'Crime')
        self.assertEqual(self.club.meeting_type, Club.MeetingType.ONLINE)
        self.assertEqual(self.club.club_type, Club.ClubType.PUBLIC)
        self.assertEqual(self.club.city, 'london')
        self.assertEqual(self.club.country, 'uk')
        self.assert_menu(response)

        
    def test_successful_club_info_update(self):
        self.client.login(username=self.owner.username, password="Password123")
        count_clubs_before = Club.objects.count()
        target_url = reverse("club_page", kwargs={"club_id": 1})
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "club_page.html")
        self.assertEqual(count_clubs_before, Club.objects.count())
        self.assert_success_message(response)
        self.club.refresh_from_db()
        self.assertEqual(self.club.name, "club2.0")
        self.assertEqual(self.club.theme, "Drama")
        self.assertEqual(self.club.meeting_type, Club.MeetingType.INPERSON)
        self.assertEqual(self.club.club_type, Club.ClubType.PRIVATE)
        self.assertEqual(self.club.city, "New York")
        self.assertEqual(self.club.country, "USA")
        self.assertEqual(self.club.owner, self.owner)
        self.assert_menu(response)


    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()
    
    def test_post_profile_redirects_when_not_logged_in(self):
       self.assert_post_redirects_when_not_logged_in()