"""Test suite for the initial genre view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin, ObjectsCreator


class InitialGenresViewTest(TestCase, LoginRedirectTester, MenuTestMixin, ObjectsCreator):
    """Test suite for the initial genre view."""

    fixtures=['bookclub/tests/fixtures/default_user.json'] 

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.url = reverse('initial_genres')

    def test_get_initial_genres_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()

    def test_initial_genres_url(self):
        self.assertEqual(self.url,'/initial_genres/')

    def test_initial_genres(self):
        self.create_test_books(4)
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_templates/initial_genres.html')
        for book_id in range(4):
            self.assertContains(response, f'genre {book_id}')  
        initial_books_url = reverse('initial_book_list')
        self.assertContains(response, initial_books_url)

    def test_initial_genres_does_not_contain_blanks(self):
        self.create_test_books(4)
        Book.objects.create(ISBN='380000059', title ='title', 
            author = ' author', genre = '')
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_templates/initial_genres.html')
        self.assertEqual(len(response.context['genres']), 4)  
    
    def test_initial_genres_does_not_contain_repeated_genres(self):
        self.create_test_books(4)
        Book.objects.create(ISBN='380000059', title ='title', 
            author = ' author', genre = 'genre 2')
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_templates/initial_genres.html')
        self.assertEqual(len(response.context['genres']), 4)  

    def test_initial_genres_is_sorted_by_frequency(self):
        self.create_test_books(4)
        Book.objects.create(ISBN='380000059', title ='title', 
            author = ' author', genre = 'genre 2')
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_templates/initial_genres.html')
        self.assertEqual(len(response.context['genres']), 4) 
        self.assertEqual(response.context['genres'][0], 'genre 2')  