"""Tests of the logged in user profile view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Club, User, Book
from bookclub.tests.helpers import LoginRedirectTester,MenuTestMixin

class ProfilePageViewTestsCase(TestCase, LoginRedirectTester,MenuTestMixin):
    """Tests of the logged in user's profile page view."""

    fixtures = [ 'bookclub/tests/fixtures/default_user.json',
                    'bookclub/tests/fixtures/other_users.json',
                    'bookclub/tests/fixtures/default_book.json',
                    'bookclub/tests/fixtures/other_books.json',
                    'bookclub/tests/fixtures/default_club.json',
                    'bookclub/tests/fixtures/other_club.json',
]
   
    def setUp(self):
        self.url = reverse('profile')
        self.user = User.objects.get(id=1)
        self.sec_user = User.objects.get(id=2)

        self.book1 = Book.objects.get(id = 1)
        self.book2 = Book.objects.get(id = 2)
        self.book3 = Book.objects.get(id = 3)
        self.book2.add_reader(self.user)
        self.book1.add_reader(self.user)
        self.book3.add_reader(self.user)

        self.club1 = Club.objects.get(id = 1)
        self.club2 = Club.objects.get(id = 2)
        self.club3 = Club.objects.get(id = 3)
        self.club1.add_member(self.user)
        self.club2.add_member(self.user)
        self.club3.add_member(self.user)

    def test_profile_page_url(self):
        self.assertEqual(self.url,'/profile/')

    def test_get_profile_page(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assert_menu(response)  
   
    def test_get_valid_user_profile_page(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('profile', kwargs={'user_id': self.sec_user.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.sec_user.username)    
        self.assertContains(response, self.sec_user.full_name())  

    def test_get_user_profile_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('profile', kwargs={'user_id': self.user.id+99999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()

    def test_get_valid_user_profile_page_with_reading_list(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.form_input = {'filter': 'Reading list'}
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assert_menu(response)  
        self.assertContains(response, self.user.username)    
        self.assertContains(response, self.user.full_name())  
        self.assertContains(response, self.book1.title)
        self.assertContains(response, self.book1.author)
        book1_url = reverse('book_details', kwargs={'book_id':self.book1.id})
        self.assertContains(response, book1_url)
        self.assertContains(response, self.book2.title)
        self.assertContains(response, self.book2.author)
        book2_url = reverse('book_details', kwargs={'book_id':self.book2.id})
        self.assertContains(response, book2_url)
        self.assertContains(response, self.book3.title)
        self.assertContains(response, self.book3.author)
        book3_url = reverse('book_details', kwargs={'book_id':self.book3.id})
        self.assertContains(response, book3_url)

    def test_get_valid_user_profile_page_with_clubs(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.form_input = {'filter': 'Clubs'}
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assert_menu(response)  
        self.assertContains(response, self.user.username)    
        self.assertContains(response, self.user.full_name())  
        self.assertContains(response, self.club1.name)    
        self.assertContains(response, self.club1.theme) 
        club1_url = reverse('club_page', kwargs={'club_id':self.club1.id})
        self.assertContains(response, club1_url)
        self.assertContains(response, self.club2.name)    
        self.assertContains(response, self.club2.theme) 
        club2_url = reverse('club_page', kwargs={'club_id':self.club2.id})
        self.assertContains(response, club2_url)
        self.assertContains(response, self.club3.name)    
        self.assertContains(response, self.club3.theme) 
        club3_url = reverse('club_page', kwargs={'club_id':self.club3.id})
        self.assertContains(response, club3_url)
