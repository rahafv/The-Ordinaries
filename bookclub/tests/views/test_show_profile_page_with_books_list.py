"""Tests of the logged in user profile view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import Book, User
from bookclub.tests.helpers import LoginRedirectTester,MenuTestMixin

class ProfilePageWithReadingListViewTestsCase(TestCase, LoginRedirectTester,MenuTestMixin):
    """Tests of the looged in user's profile page view."""

    fixtures = [ 'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/default_book.json',
                'bookclub/tests/fixtures/other_books.json',
            ]
   
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.book1 = Book.objects.get(id = 1)
        self.book2 = Book.objects.get(id = 2)
        self.book3 = Book.objects.get(id = 3)
        self.book2.add_reader(self.user)
        self.book1.add_reader(self.user)
        self.book3.add_reader(self.user2)
        self.url = reverse('profile_reading_list', kwargs = {'user_id':self.user2.id})
       
    def test_profile_page_with_reading_list_url(self):
        self.client.login(username = self.user.username, password = "Password123")
        self.assertEqual(self.url,'/profile/2/reading_list')

    def test_get_valid_user_profile_page_with_reading_list(self):
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
        self.assertContains(response, self.book3.title)
        self.assertContains(response, self.book3.author)
        self.assertNotContains(response, self.book2.title)    
        self.assertNotContains(response, self.book2.author) 
        self.assertNotContains(response, self.book1.title)    
        self.assertNotContains(response, self.book1.author) 
        book3_url = reverse('book_details', kwargs={'book_id':self.book3.id})
        self.assertContains(response, book3_url)
        
          

    def test_get_user_profile_page_with_request_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('profile', kwargs={'user_id': self.user.id})
        target_url = reverse('profile')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.user.username)    
        self.assertContains(response, self.user.full_name()) 
    
    def test_get_user_profile_page_reading_list_with_request_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('profile_reading_list', kwargs={'user_id': self.user.id})
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
        self.assertContains(response, self.book1.title)
        self.assertContains(response, self.book1.author)
        self.assertContains(response, self.book2.title)
        self.assertContains(response, self.book2.author)
        self.assertNotContains(response, self.book3.title)    
        self.assertNotContains(response, self.book3.author) 
        book2_url = reverse('book_details', kwargs={'book_id':self.book2.id})
        self.assertContains(response, book2_url)
        book1_url = reverse('book_details', kwargs={'book_id':self.book1.id})
        self.assertContains(response, book1_url)

    def test_get_profile_page_with_reading_list_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()