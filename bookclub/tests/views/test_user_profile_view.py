"""Tests of the logged in user profile view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import LoginRedirectTester,MenuTestMixin

class ProfilePageViewTestsCase(TestCase, LoginRedirectTester,MenuTestMixin):
    """Tests of the looged in user's profile page view."""

    fixtures = [ 'bookclub/tests/fixtures/default_user.json',
                    'bookclub/tests/fixtures/other_users.json',
                    'bookclub/tests/fixtures/default_book.json',
                    'bookclub/tests/fixtures/other_books.json',
]
   
    def setUp(self):
        self.url = reverse('profile')
        self.user = User.objects.get(id=1)
        self.user2 = User.objects.get(id=2)
        self.book = Book.objects.get(id = 2)

    def test_profile_page_url(self):
        self.assertEqual(self.url,'/profile/')

    def test_get_profile_page(self):
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
   
    def test_get_valid_user_profile_page(self):
        self.client.login(username=self.user.username, password='Password123')
        self.book.add_reader(self.user2)
        self.book.save()
        self.url = reverse('profile', kwargs={'user_id': self.user2.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.user2.username)    
        self.assertContains(response, self.user2.full_name())  
        self.assertNotContains(response, self.user.username)    
        self.assertNotContains(response, self.user.full_name())
        self.assertContains(response, self.book.title)    
        self.assertContains(response, self.book.author)
        book_url = reverse('book_details', kwargs={'book_id':self.book.id})
        self.assertContains(response, book_url)     

    def test_get_user_profile_page_with_request_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('profile', kwargs={'user_id': self.user.id})
        target_url = reverse('profile')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile_page.html')
        self.assertContains(response, self.user.username)    
        self.assertContains(response, self.user.full_name()) 

    def test_get_profile_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()