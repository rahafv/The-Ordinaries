"""Test suite for the search page view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import ClubsSortForm, UsersSortForm, BooksSortForm
from bookclub.models import User, Club, Book
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin

class SearchPageTest(TestCase, LoginRedirectTester,MenuTestMixin):
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
        self.assertEqual(self.url,f'/search_page/')

    def test_search_users_with_name(self):
        self._create_test_users()
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
        self._create_test_users()
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
        self._create_test_clubs()
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
        self._create_test_clubs()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.club_location_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        self.assertContains(response, "uk")
        self.assertNotContains(response, "usa")
        self.assert_menu(response)

    def test_search_books_with_title(self):
        self._create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.book_title_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        self.assertContains(response, "uio")
        self.assertNotContains(response, "xyz")
        self.assert_menu(response)

    def test_search_books_with_author(self):
        self._create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.book_author_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        self.assertContains(response, "James")
        self.assertNotContains(response, "joe")
        self.assert_menu(response)

    def test_search_books_with_genre(self):
        self._create_test_books()
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


    def _create_test_users(self, user_count=6):
        for user_id in range(user_count):
            if user_id < 3: 
                first_name = "joe"
                country = "uk"
            else: 
                first_name = "jane"
                country= "USA"

            User.objects.create(
                first_name = first_name,
                last_name = f'last{user_id}', 
                username=f'{first_name}last{user_id}',
                email = f'{first_name}last{user_id}@example.org', 
                email_verified = True, 
                city = "london",
                country = country

            )

    def _create_test_clubs(self, club_count=6):
        for club_id in range(club_count):
            if club_id < 3: 
                name = "The"
                country = "uk"
            else: 
                name = "american"
                country = "usa"
            Club.objects.create(owner = self.user,
                name =f'{name}{club_id}',
                theme=f'theme{club_id}',
                meeting_type =Club.MeetingType.INPERSON,
                city=f'city{club_id}',
                country=country,
            )

    def _create_test_books(self, book_count=6):
        isbn_num = ['0425176428', '0002005018', '0060973129','0374157065', '0393045218', '0399135782','034545104X'
                    ,'155061224','446520802','052165615X','521795028', '2080674722','3257224281','600570967','038550120X',
                    '342310538', '425115801','449006522','553561618', '055356451X','786013990','786014512','60517794','451192001','609801279',
                    '671537458','679776818','943066433','1570231028','1885408226','747558167','3442437407','033390804X','3596218098','684867621',
                    '451166892','8440682697','034544003X','380000059','380711524']
        for book_id in range(book_count):
            if book_id < 3: 
                title = 'uio'
                author = 'James'
                genre = 'fiction'
            else: 
                title = 'xyz'
                author = 'joe'
                genre = 'non fiction'

            Book.objects.create(
                ISBN = isbn_num[book_id],
                title =title,
                author = author, 
            )


    
