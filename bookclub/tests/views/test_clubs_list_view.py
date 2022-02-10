from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester , MenueTestMixin
from system import settings

class ClubsListTest(TestCase, LoginRedirectTester ,MenueTestMixin ):

    fixtures=[
                'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_club.json',
                'bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.club = Club.objects.get(id=1)
        self.other_club = Club.objects.get(id=2)
        self.url = reverse('clubs_list')
        
    def test_clubs_list_url(self):
        self.assertEqual(self.url,f'/clubs/')

    def test_get_clubs_list_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()

    def test_get_user_clubs_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.club.add_member(self.user)
        self.other_club.add_member(self.user)
        self.url = reverse('clubs_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertContains(response, f'club1')
        self.assertContains(response, f'Crime')
        self.assertContains(response, f'club2')
        self.assertContains(response, f'Fictional superheros')
        clubs_url = reverse('clubs_list')
        self.assertContains(response, clubs_url)
        self.assert_menu(response)

    def test_get_clubs_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE-2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        for club_id in range(settings.CLUBS_PER_PAGE-2):
            self.assertContains(response, f'club{club_id}')
            self.assertContains(response, f'theme{club_id}')
            clubs_url = reverse('clubs_list')
            self.assertContains(response, clubs_url)
        self.assert_menu(response)

    def test_get_clubs_list_with_pagination(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE*2+3)
        response = self.client.get(self.url)
        self.assert_menu(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['clubs']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('clubs_list') + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['clubs']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('clubs_list') + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        page_obj = response.context['clubs']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('clubs_list') + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertEqual(len(response.context['clubs']), 5)
        page_obj = response.context['clubs']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
        self.assert_menu(response)


    def _create_test_clubs(self, club_count=10):
        for club_id in range(club_count):
            Club.objects.create(owner = self.user,
                name =f'club{club_id}',
                theme=f'theme{club_id}',
                meeting_type =Club.MeetingType.INPERSON,
                city=f'city{club_id}',
                country=f'country {club_id}',
            )