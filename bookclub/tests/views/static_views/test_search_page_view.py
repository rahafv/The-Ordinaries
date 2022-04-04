"""Test suite for the search page view."""
from bookclub.models import User
from bookclub.tests.helpers import LoginRedirectTester, MenuTestMixin, ObjectsCreator
from django.test import TestCase
from django.urls import reverse


class SearchPageTest(TestCase, LoginRedirectTester,MenuTestMixin, ObjectsCreator):
    """Test suite for the search page view."""

    fixtures=['bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.url = reverse('search_page')
        self.BOOKS_PER_PAGE = 15

        self.invalid_form_input = {
            'sort': 'name', 
            'category': 'club-name',
            'searched':'The',
            }
        self.user_name_form_input = {
            'category': 'user-name',
            'searched':'joe',
        }
        self.user_country_form_input = {
            'category': 'user-location',
            'searched':'uk',
        }
        self.club_name_form_input = {
            'category': 'club-name',
            'searched':'The',
        }
        self.club_location_form_input = {
            'category': 'club-location',
            'searched':'uk',
        }
        self.book_title_form_input = {
            'category': 'book-title',
            'searched':'uio',
        }
        self.book_author_form_input = {
            'category': 'book-author',
            'searched':'James',
        }
        self.book_genre_form_input = {
            'category': 'book-genre',
            'searched':'fiction',
        }


    def test_get_books_list_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()

    def test_search_page_url(self):
        self.assertEqual(self.url,f'/search/')

    def test_search_users_with_name(self):
        self.create_test_search_users()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.user_name_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        for user_id in range(3):
            self.assertContains(response, f'joelast{user_id}')
        for user_id in range(3, 6): 
            self.assertNotContains(response, f'janelast{user_id}')
        self.assert_menu(response)
       
    
    def test_search_users_with_country(self):
        self.create_test_search_users()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.user_country_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        for user_id in range(3):
            self.assertContains(response, f'joelast{user_id}')
        for user_id in range(3, 6): 
            self.assertNotContains(response, f'janelast{user_id}')
        self.assert_menu(response)


    def test_search_club_with_name(self):
        self.create_test_search_clubs()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.club_name_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        for club_id in range(3):
            self.assertContains(response, f'The{club_id}')
        for club_id in range(3, 6):
            self.assertNotContains(response, f'or{club_id}')
        self.assert_menu(response)

    def test_search_club_with_country(self):
        self.create_test_search_clubs()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.club_location_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        self.assertContains(response, "uk")
        self.assertNotContains(response, "usa")
        self.assert_menu(response)

    def test_search_books_with_title(self):
        self.create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.book_title_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        self.assertContains(response, "uio")
        self.assertNotContains(response, "xyz")
        self.assert_menu(response)

    def test_search_books_with_author(self):
        self.create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.book_author_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        self.assertContains(response, "James")
        self.assertNotContains(response, "joe")
        self.assert_menu(response)

    def test_search_books_with_genre(self):
        self.create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.book_genre_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        self.assertContains(response, "fiction")
        self.assertNotContains(response, "non fiction")
        self.assert_menu(response)

    def test_search_with_empty_str(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user_name_form_input['searched'] = ''
        response = self.client.get(self.url, self.user_name_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        self.assertContains(response, "You forgot to search!")
        self.assert_menu(response)

    def test_search_with_invalid_sort_form(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user_name_form_input['searched'] = ''
        response = self.client.get(self.url, self.invalid_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assert_menu(response)

    def test_search_with_no_category(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'static_templates/404_page.html')


    
