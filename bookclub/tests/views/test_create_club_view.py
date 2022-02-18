"""Tests of the create club view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import CreateClubForm
from bookclub.models import Club, User
from bookclub.tests.helpers import LoginRedirectTester , MenueTestMixin

class CreateClubViewTestCase(TestCase, LoginRedirectTester,MenueTestMixin):
    """Test suite for the create club view."""

    fixtures = ["bookclub/tests/fixtures/default_user.json"]

    def setUp(self):
        self.url = reverse("create_club")
        self.user = User.objects.get(id=1)
        self.form_input = {
            'name': 'Club1',
            'theme': 'Fiction',
<<<<<<< HEAD
=======
            'meeting_type': Club.MeetingType.INPERSON,
            'club_type': Club.ClubType.PRIVATE,
>>>>>>> 4155aafe82568a5db1ad8ad471ebb6235b9c50cb
            'city': 'nyc', 
            'country': 'usa'
        }

    def test_create_club_url(self):
        self.assertEqual(self.url, "/create_club/")

    def test_create_club_get(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_club.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertFalse(form.is_bound)
        self.assert_menu(response)

    def test_create_club_successful(self):
        self.client.login(username=self.user.username, password="Password123")
        count_clubs_before = Club.objects.count()
        target_url = reverse("club_page", kwargs={"club_id": 1})
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "club_page.html")
        self.assertEqual(count_clubs_before + 1, Club.objects.count())
        club = Club.objects.get(name="Club1")
        self.assertEqual(club.name, "Club1")
        self.assertEqual(club.theme, "Fiction")
<<<<<<< HEAD
=======
        self.assertEqual(club.meeting_type, Club.MeetingType.INPERSON)
        self.assertEqual(club.club_type, Club.ClubType.PRIVATE)
>>>>>>> 4155aafe82568a5db1ad8ad471ebb6235b9c50cb
        self.assertEqual(club.city, "nyc")
        self.assertEqual(club.country, "usa")
        owner = User.objects.get(username="johndoe")
        self.assertEqual(club.owner, owner)
        self.assert_menu(response)

    def test_create_club_unsuccessful(self):
        self.client.login(username=self.user.username, password="Password123")
        count_clubs_before = Club.objects.count()
        self.form_input["name"] = ""
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(count_clubs_before, Club.objects.count())
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertTemplateUsed(response, "create_club.html")
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assert_menu(response)

    def test_get_create_club_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_post_create_club_redirects_when_not_logged_in(self):
        self.assert_post_redirects_when_not_logged_in()