"""Tests of the logged in user's profile page with clubs list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester,MenuTestMixin

class ProfilePageWithClubsListViewTestsCase(TestCase, LoginRedirectTester,MenuTestMixin):
    """Tests of the logged in user's profile page with clubs list view."""

    fixtures = [ 'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_club.json',
            ]
   
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.club1 = Club.objects.get(id = 1)
        self.club2 = Club.objects.get(id = 2)
        self.club3 = Club.objects.get(id = 3)
        self.club1.add_member(self.user2)
        self.club2.add_member(self.user2)
        self.club3.add_member(self.user2)
        self.url = reverse('profile_clubs', kwargs = {'user_id':self.user2.id})
       
    def test_profile_page_with_clubs_list_url(self):
        self.assertEqual(self.url,'/profile/2/clubs/')

    def test_get_valid_user_profile_page_with_club_list(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        menu_urls= [
            reverse('profile'), reverse('password'), reverse('log_out')
        ]
        for url in menu_urls:
            self.assertContains(response, url)  
        self.assert_menu(response)  
        self.assertContains(response, self.user2.username)    
        self.assertContains(response, self.user2.full_name())  
        self.assertNotContains(response, self.user.username)    
        self.assertNotContains(response, self.user.full_name())
        self.assertContains(response, self.club3.name)
        self.assertContains(response, self.club3.theme)
        clubs_url = reverse('clubs_list')
        self.assertContains(response, clubs_url)
        self.assertContains(response, self.club2.name)    
        self.assertContains(response, self.club2.theme) 
        self.assertContains(response, self.club1.name)    
        self.assertContains(response, self.club1.theme) 
        club1_url = reverse('club_page', kwargs={'club_id':self.club1.id})
        self.assertContains(response, club1_url)
        club2_url = reverse('club_page', kwargs={'club_id':self.club2.id})
        self.assertContains(response, club2_url)
          

    def test_get_user_profile_page_with_request_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('profile', kwargs={'user_id': self.user.id})
        target_url = reverse('profile')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.user.username)    
        self.assertContains(response, self.user.full_name())
        self.assertNotContains(response, self.user2.username)    
        self.assertNotContains(response, self.user2.full_name())  
    
    def test_get_user_profile_page__with_empty_club_list_with_request_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('profile_clubs', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.user.username) 
        self.assertContains(response, self.user.email)       
        self.assertContains(response, self.user.full_name()) 
        menu_urls= [
            reverse('profile'), reverse('password'), reverse('log_out')
        ]
        for url in menu_urls:
            self.assertContains(response, url)  
        self.assert_menu(response)  
        self.assertNotContains(response, self.user2.username)    
        self.assertNotContains(response, self.user2.full_name())  
        self.assertNotContains(response, self.club3.name)
        self.assertNotContains(response, self.club3.theme)
        self.assertNotContains(response, self.club2.name)    
        self.assertNotContains(response, self.club2.theme) 
        self.assertNotContains(response, self.club1.name)    
        self.assertNotContains(response, self.club1.theme) 

    def test_get_user_profile_page_club_list_with_added_club_with_request_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.club1.add_member(self.user)
        self.club1.save()
        self.url = reverse('profile_clubs', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.user.username) 
        self.assertContains(response, self.user.email)       
        self.assertContains(response, self.user.full_name()) 
        menu_urls= [
            reverse('profile'), reverse('password'), reverse('log_out')
        ]
        for url in menu_urls:
            self.assertContains(response, url)  
        self.assert_menu(response)  
        self.assertNotContains(response, self.user2.username)    
        self.assertNotContains(response, self.user2.full_name())  
        self.assertNotContains(response, self.club3.name)
        self.assertNotContains(response, self.club3.theme)
        self.assertNotContains(response, self.club2.name)    
        self.assertNotContains(response, self.club2.theme) 
        self.assertContains(response, self.club1.name)    
        self.assertContains(response, self.club1.theme) 
        club1_url = reverse('club_page', kwargs={'club_id':self.club1.id})
        self.assertContains(response, club1_url)

    def test_get_user_profile_page_clubs_with_invalid_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('profile_clubs', kwargs={'user_id': 0})
        response = self.client.get(self.url, follow=True)
        self.assertEquals(response.status_code, 404)
        self.assertTemplateUsed(response, '404_page.html') 

    def test_get_profile_club_page_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()