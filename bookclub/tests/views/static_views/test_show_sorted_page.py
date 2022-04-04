"""Tests of the sorted search page view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.forms import ClubsSortForm, UsersSortForm, BooksSortForm
from bookclub.models import User, Club, Book
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin, ObjectsCreator

class SortedSearchPageTest(TestCase, LoginRedirectTester,MenuTestMixin, ObjectsCreator):
    """Tests of the sorted search page view."""

    fixtures=['bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.BOOKS_PER_PAGE = 15
        self.books_sort_form_input = {'sort': BooksSortForm.DESC_RATING}
        self.user_sort_form_input = {'sort': UsersSortForm.ASCENDING}
        self.clubs_sort_form_input = {'sort':ClubsSortForm.ASC_DATE}
        self.invalid_form_input = {'sort': 'name'}

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
        
        self.url = reverse('show_sorted', kwargs={"searched": self.user_name_form_input["searched"], "label":self.user_name_form_input["category"]})

    def test_get_show_sorted_list_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()

    def test_show_sorted_page_url(self):
        self.assertEqual(self.url,f'/search/{"joe"}/{"user-name"}/')

    def test_sort_users_with_name_asc_by_name(self):
        self.create_test_search_users()
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url,self.user_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, UsersSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_asc')
        for user_id in range(3):
            self.assertContains(response, f'joelast{user_id}')
        for user_id in range(3, 6): 
            self.assertNotContains(response, f'janelast{user_id}')  
        self.assert_menu(response)
       
    def test_sort_users_with_country_desc_by_name(self):
        self.create_test_search_users()
        self.client.login(username=self.user.username, password='Password123')
        self.user_sort_form_input["sort"] = UsersSortForm.DESCENDING
        target_url = reverse('show_sorted', kwargs={"searched": self.user_country_form_input['searched'], "label": self.user_country_form_input["category"]})
        response = self.client.get(target_url,self.user_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, UsersSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')
        for user_id in range(3):
            self.assertContains(response, f'joelast{user_id}')
        for user_id in range(3, 6): 
            self.assertNotContains(response, f'janelast{user_id}') 
        self.assert_menu(response)

    def test_sort_club_with_name_asc_by_date(self):
        self.create_test_search_clubs()
        self.client.login(username=self.user.username, password='Password123')
        target_url = reverse('show_sorted', kwargs={"searched": self.club_name_form_input['searched'], "label": self.club_name_form_input["category"]})
        response = self.client.get(target_url,self.clubs_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'date_asc')
        for club_id in range(3):
            self.assertContains(response, f'The{club_id}')
        for club_id in range(3, 6):
            self.assertNotContains(response, f'or{club_id}') 
        self.assert_menu(response)
        
    def test_sort_club_with_country_desc_by_date(self):
        self.create_test_clubs()
        self.client.login(username=self.user.username, password='Password123')
        self.clubs_sort_form_input["sort"] = ClubsSortForm.DESC_DATE
        target_url = reverse('show_sorted', kwargs={"searched": self.club_location_form_input['searched'], "label": self.club_location_form_input["category"]})
        response = self.client.get(target_url,self.clubs_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'date_desc')
        self.assertContains(response, "uk")
        self.assertNotContains(response, "usa") 
        self.assert_menu(response)
    
    def test_sort_club_with_country_asc_by_name(self):
        self.create_test_clubs()
        self.client.login(username=self.user.username, password='Password123')
        self.clubs_sort_form_input["sort"] = ClubsSortForm.ASC_NAME
        target_url = reverse('show_sorted', kwargs={"searched": self.club_location_form_input['searched'], "label": self.club_location_form_input["category"]})
        response = self.client.get(target_url,self.clubs_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_asc')
        self.assertContains(response, "uk")
        self.assertNotContains(response, "usa") 
        self.assert_menu(response)
        
    def test_sort_club_with_country_desc_by_name(self):
        self.create_test_clubs()
        self.client.login(username=self.user.username, password='Password123')
        self.clubs_sort_form_input["sort"] = ClubsSortForm.DESC_NAME
        target_url = reverse('show_sorted', kwargs={"searched": self.club_location_form_input['searched'], "label": self.club_location_form_input["category"]})
        response = self.client.get(target_url,self.clubs_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, ClubsSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')
        self.assertContains(response, "uk")
        self.assertNotContains(response, "usa") 
        self.assert_menu(response)   

    def test_sort_books_with_title_desc_by_name(self):
        self.create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        self.books_sort_form_input["sort"] = BooksSortForm.DESC_NAME
        target_url = reverse('show_sorted', kwargs={"searched": self.book_title_form_input['searched'], "label": self.book_title_form_input["category"]})
        response = self.client.get(target_url,self.books_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc') 
        self.assertContains(response, "uio")
        self.assertNotContains(response, "xyz")
        self.assert_menu(response)

    def test_sort_books_with_author_asc_by_name(self):
        self.create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        self.books_sort_form_input["sort"] = BooksSortForm.ASC_NAME
        target_url = reverse('show_sorted', kwargs={"searched": self.book_author_form_input['searched'], "label": self.book_author_form_input["category"]})
        response = self.client.get(target_url,self.books_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_asc')
        self.assertContains(response, "James")
        self.assertNotContains(response, "joe") 
        self.assert_menu(response) 

    def test_sort_books_with_title_asc_by_rating(self):
        self.create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        self.books_sort_form_input["sort"] = BooksSortForm.ASC_RATING
        target_url = reverse('show_sorted', kwargs={"searched": self.book_title_form_input['searched'], "label": self.book_title_form_input["category"]})
        response = self.client.get(target_url,self.books_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'rating_asc')
        self.assert_menu(response) 

    def test_sort_books_with_title_desc_by_rating(self):
        self.create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        self.books_sort_form_input["sort"] = BooksSortForm.DESC_RATING
        target_url = reverse('show_sorted', kwargs={"searched": self.book_title_form_input['searched'], "label": self.book_title_form_input["category"]})
        response = self.client.get(target_url,self.books_sort_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'rating_desc')
        self.assert_menu(response) 
    
    def test_post_search_sort_with_empty_str(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('show_sorted', kwargs={"searched": self.book_author_form_input['searched'], "label": self.book_author_form_input["category"]})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        self.assertContains(response, "You forgot to search!")
        self.assert_menu(response)

    def test_invalid_form(self):
        self.create_test_books()
        self.client.login(username=self.user.username, password='Password123')
        target_url = reverse('show_sorted', kwargs={"searched": self.book_author_form_input['searched'], "label": self.book_author_form_input["category"]})
        response = self.client.get(target_url,self.invalid_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'static_templates/search_page.html')
        form = response.context['form']
        self.assertFalse(form.is_valid())  