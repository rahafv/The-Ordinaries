from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.forms import NameAndDateSortForm
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin
from system import settings

class OwnedClubsListTest(TestCase, LoginRedirectTester,MenuTestMixin):

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
        self.url = reverse('owned_clubs_list')
        self.form_input = {
            'sort':NameAndDateSortForm.DESC_DATE,
    }
        
    def test_clubs_list_url(self):
        self.assertEqual(self.url,f'/owned/')

    def test_get_clubs_list_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()

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
        self.assertTrue(isinstance(form, NameAndDateSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'date_desc')   
        self.assert_menu(response)

