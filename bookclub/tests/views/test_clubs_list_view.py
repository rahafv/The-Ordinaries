from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.forms import ClubsSortForm
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin
from system import settings

class ClubsListTest(TestCase, LoginRedirectTester ,MenuTestMixin ):

    fixtures=[
                'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_club.json',
                'bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.club = Club.objects.get(id=1)
        self.other_club = Club.objects.get(id=2)
        self.num_of_clubs = Club.objects.count()
        self.url = reverse('clubs_list')
        self.form_input = {
            'sort':ClubsSortForm.DESC_DATE,
            'privacy':'all',
            'ownership':'all'
        }
        
    def test_clubs_list_url(self):
        self.assertEqual(self.url,f'/clubs/')


    def test_get_user_clubs_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.club.add_member(self.user)
        self.other_club.add_member(self.user)
        self.url = reverse('clubs_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertContains(response, f'club1')
        self.assertContains(response, f'Crime')
        self.assertContains(response, f'club2')
        self.assertContains(response, f'Fictional superheros')
        clubs_url = reverse('clubs_list')
        self.assertContains(response, clubs_url)
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'date_desc')   
        self.assert_menu(response)

    def test_get_clubs_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE-self.num_of_clubs)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        for club_id in range(settings.CLUBS_PER_PAGE-self.num_of_clubs):
            self.assertContains(response, f'club{club_id}')
            self.assertContains(response, f'theme{club_id}')
            clubs_url = reverse('clubs_list')
            self.assertContains(response, clubs_url)
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'date_desc')   
        self.assert_menu(response)
    
    def test_get_clubs_list_descending_date(self):
        self.form_input['sort'] = ClubsSortForm.DESC_DATE
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE-self.num_of_clubs)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        for club_id in range(settings.CLUBS_PER_PAGE-self.num_of_clubs):
            self.assertContains(response, f'club{club_id}')
            self.assertContains(response, f'theme{club_id}')
            clubs_url = reverse('clubs_list')
            self.assertContains(response, clubs_url)
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'date_desc')   
        self.assert_menu(response)

    def test_get_clubs_list_ascending_date(self):
        self.form_input['sort'] = ClubsSortForm.ASC_DATE
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE-self.num_of_clubs)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        for club_id in range(settings.CLUBS_PER_PAGE-self.num_of_clubs):
            self.assertContains(response, f'club{club_id}')
            self.assertContains(response, f'theme{club_id}')
            clubs_url = reverse('clubs_list')
            self.assertContains(response, clubs_url)
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'date_asc')   
        self.assert_menu(response)


    def test_get_clubs_list_ascending_name(self):
        self.form_input['sort'] = ClubsSortForm.ASC_NAME
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE-self.num_of_clubs)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        for club_id in range(settings.CLUBS_PER_PAGE-self.num_of_clubs):
            self.assertContains(response, f'club{club_id}')
            self.assertContains(response, f'theme{club_id}')
            clubs_url = reverse('clubs_list')
            self.assertContains(response, clubs_url)
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_asc')   
        self.assert_menu(response)
    
    def test_get_clubs_list_descending_name(self):
        self.form_input['sort'] = ClubsSortForm.DESC_NAME
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE-self.num_of_clubs)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        self.assertEqual(len(response.context['clubs']), settings.CLUBS_PER_PAGE)
        for club_id in range(settings.CLUBS_PER_PAGE-self.num_of_clubs):
            self.assertContains(response, f'club{club_id}')
            self.assertContains(response, f'theme{club_id}')
            clubs_url = reverse('clubs_list')
            self.assertContains(response, clubs_url)
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')   
        self.assert_menu(response)

    def test_get_clubs_list_with_pagination(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE*2+self.num_of_clubs)
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
        self.assertEqual(len(response.context['clubs']), 8)
        page_obj = response.context['clubs']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
        self.assert_menu(response)


    def _create_test_clubs(self, club_count=10):
        for club_id in range(club_count):
            Club.objects.create(owner = self.user,
                name =f'club{club_id}',
                theme=f'theme{club_id}',
                city=f'city{club_id}',
                country=f'country {club_id}',
            )

    def test_get_private_clubs_list(self):
        self.form_input['privacy'] = 'private'
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE-self.num_of_clubs)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        form = response.context['form']
        num_of_private_clubs = Club.objects.filter(club_type='Private').count()
        self.assertEqual(len(response.context['clubs']), num_of_private_clubs)
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assert_menu(response)

    def test_get_public_clubs_list(self):
        self.form_input['privacy'] = 'public'
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE-self.num_of_clubs)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        form = response.context['form']
        num_of_public_clubs = Club.objects.filter(club_type='Public').count()
        self.assertEqual(len(response.context['clubs']), num_of_public_clubs)
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assert_menu(response)

    def test_get_owned_clubs_list(self):
        self.form_input['ownership'] = 'owned'
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_clubs(settings.CLUBS_PER_PAGE-self.num_of_clubs)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs.html')
        form = response.context['form']
        num_of_owned_clubs = Club.objects.filter(owner=self.user).count()
        self.assertEqual(len(response.context['clubs']), num_of_owned_clubs)
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assert_menu(response)