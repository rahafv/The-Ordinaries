"""Tests of the create club view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import CreateClubForm
from bookclub.models import Club, User


class CreateClubViewTestCase(TestCase):
    """Test suite for the create club view."""

    fixtures = ["bookclub/tests/fixtures/default_user.json"]

    def setUp(self):
        self.url = reverse("create_club")
        self.form_input = {
            'name': 'Club1',
            'theme': 'Fiction',
            'meeting_type': Club.MeetingType.INPERSON,
            'city': 'nyc', 
            'country': 'usa'
        }

    def test_create_club_url(self):
        self.assertEqual(self.url, "/create_club/")

    def test_create_club_get(self):
        self.client.login(username="johndoe", password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_club.html")
        form = response.context["form"]
        self.assertTrue(isinstance(form, CreateClubForm))
        self.assertFalse(form.is_bound)

    def test_create_club_successful(self):
        self.client.login(username="johndoe", password="Password123")
        count_clubs_before = Club.objects.count()
        target_url = reverse("club_page", kwargs={"club_id": 1})
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "club_page.html")
        self.assertEqual(count_clubs_before + 1, Club.objects.count())
        club = Club.objects.get(name="Club1")
        self.assertEqual(club.name, "Club1")
        self.assertEqual(club.theme, "Fiction")
        self.assertEqual(club.meeting_type, Club.MeetingType.INPERSON)
        self.assertEqual(club.city, "nyc")
        self.assertEqual(club.country, "usa")
        owner = User.objects.get(username="johndoe")
        self.assertEqual(club.owner, owner)

    def test_create_club_unsuccessful(self):
        self.client.login(username="johndoe", password="Password123")
        count_clubs_before = Club.objects.count()
        self.form_input["name"] = ""
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(count_clubs_before, Club.objects.count())
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertTrue(form.is_bound)
        self.assertTemplateUsed(response, "create_club.html")
        self.assertTrue(isinstance(form, CreateClubForm))

    # def test_get_create_club_redirects_when_not_logged_in(self):
    #     target_url = reverse("log_in") + f"?next={self.url}"
    #     response = self.client.get(self.url, follow=True)
    #     self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, "log_in.html")

    # def test_post_create_club_redirects_when_not_logged_in(self):
    #     target_url = reverse("log_in") + f"?next={self.url}"
    #     response = self.client.post(self.url, self.form_input, follow=True)
    #     self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, "log_in.html")