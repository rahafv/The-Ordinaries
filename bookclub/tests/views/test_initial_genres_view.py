from django.test import TestCase
from django.urls import reverse
from bookclub.forms import ClubsSortForm, UsersSortForm, BooksSortForm
from bookclub.models import User, Club, Book
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin
from system import settings

class InitialGenresViewTest(TestCase, LoginRedirectTester,MenuTestMixin):

    fixtures=['bookclub/tests/fixtures/default_user.json'] 

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.url = reverse('initial_genres')

    def test_get_initial_genres_redirects_when_not_logged_in(self):
       self.assert_redirects_when_not_logged_in()

    def test_initial_genres_url(self):
        self.assertEqual(self.url,'/initial_book_list/genres')

    def test_initial_genres(self):
        self._create_test_books(4)
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'initial_genres.html')
        for book_id in range(4):
            self.assertContains(response, f'genre {book_id}')  

    def test_initial_genres_does_not_contain_blanks(self):
        self._create_test_books(4)
        Book.objects.create(ISBN='380000059', title ='title', 
            author = ' author', genre = '')
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'initial_genres.html')
        self.assertEqual(len(response.context['genres']), 4)  
    
    def test_initial_genres_does_not_contain_repeated_genres(self):
        self._create_test_books(4)
        Book.objects.create(ISBN='380000059', title ='title', 
            author = ' author', genre = 'genre 2')
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'initial_genres.html')
        self.assertEqual(len(response.context['genres']), 4)  

    def test_initial_genres_is_sorted_by_frequency(self):
        self._create_test_books(4)
        Book.objects.create(ISBN='380000059', title ='title', 
            author = ' author', genre = 'genre 2')
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'initial_genres.html')
        self.assertEqual(len(response.context['genres']), 4) 
        self.assertEqual(response.context['genres'][0], 'genre 2') 

       
    # def test_sort_users_with_country_desc_by_name(self):
    #     self._create_test_users()
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.user_sort_form_input["sort"] = UsersSortForm.DESCENDING
    #     target_url = reverse('show_sorted', kwargs={"searched": self.user_country_form_input['searched'], "label": self.user_country_form_input["category"]})
    #     response = self.client.get(target_url,self.user_sort_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form= response.context['form']
    #     self.assertTrue(isinstance(form, UsersSortForm)) 
    #     self.assertTrue(form.is_valid())
    #     self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')
    #     for user_id in range(3):
    #         self.assertContains(response, f'joelast{user_id}')
    #     for user_id in range(3, 6): 
    #         self.assertNotContains(response, f'janelast{user_id}') 
    #     self.assert_menu(response)

    # def test_sort_club_with_name_asc_by_date(self):
    #     self._create_test_clubs()
    #     self.client.login(username=self.user.username, password='Password123')
    #     target_url = reverse('show_sorted', kwargs={"searched": self.club_name_form_input['searched'], "label": self.club_name_form_input["category"]})
    #     response = self.client.get(target_url,self.clubs_sort_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form= response.context['form']
    #     self.assertTrue(isinstance(form, ClubsSortForm)) 
    #     self.assertTrue(form.is_valid())
    #     self.assertEqual(form.cleaned_data.get('sort'), 'date_asc')
    #     for club_id in range(3):
    #         self.assertContains(response, f'The{club_id}')
    #     for club_id in range(3, 6):
    #         self.assertNotContains(response, f'or{club_id}') 
    #     self.assert_menu(response)
        
    # def test_sort_club_with_country_desc_by_date(self):
    #     self._create_test_clubs()
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.clubs_sort_form_input["sort"] = ClubsSortForm.DESC_DATE
    #     target_url = reverse('show_sorted', kwargs={"searched": self.club_location_form_input['searched'], "label": self.club_location_form_input["category"]})
    #     response = self.client.get(target_url,self.clubs_sort_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form= response.context['form']
    #     self.assertTrue(isinstance(form, ClubsSortForm)) 
    #     self.assertTrue(form.is_valid())
    #     self.assertEqual(form.cleaned_data.get('sort'), 'date_desc')
    #     self.assertContains(response, "uk")
    #     self.assertNotContains(response, "usa") 
    #     self.assert_menu(response)
    
    # def test_sort_club_with_country_asc_by_name(self):
    #     self._create_test_clubs()
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.clubs_sort_form_input["sort"] = ClubsSortForm.ASC_NAME
    #     target_url = reverse('show_sorted', kwargs={"searched": self.club_location_form_input['searched'], "label": self.club_location_form_input["category"]})
    #     response = self.client.get(target_url,self.clubs_sort_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form= response.context['form']
    #     self.assertTrue(isinstance(form, ClubsSortForm)) 
    #     self.assertTrue(form.is_valid())
    #     self.assertEqual(form.cleaned_data.get('sort'), 'name_asc')
    #     self.assertContains(response, "uk")
    #     self.assertNotContains(response, "usa") 
    #     self.assert_menu(response)
        
    # def test_sort_club_with_country_desc_by_name(self):
    #     self._create_test_clubs()
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.clubs_sort_form_input["sort"] = ClubsSortForm.DESC_NAME
    #     target_url = reverse('show_sorted', kwargs={"searched": self.club_location_form_input['searched'], "label": self.club_location_form_input["category"]})
    #     response = self.client.get(target_url,self.clubs_sort_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form= response.context['form']
    #     self.assertTrue(isinstance(form, ClubsSortForm)) 
    #     self.assertTrue(form.is_valid())
    #     self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')
    #     self.assertContains(response, "uk")
    #     self.assertNotContains(response, "usa") 
    #     self.assert_menu(response)   

    # def test_sort_books_with_title_desc_by_name(self):
    #     self._create_test_books()
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.books_sort_form_input["sort"] = BooksSortForm.DESC_NAME
    #     target_url = reverse('show_sorted', kwargs={"searched": self.book_title_form_input['searched'], "label": self.book_title_form_input["category"]})
    #     response = self.client.get(target_url,self.books_sort_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form= response.context['form']
    #     self.assertTrue(isinstance(form, BooksSortForm)) 
    #     self.assertTrue(form.is_valid())
    #     self.assertEqual(form.cleaned_data.get('sort'), 'name_desc') 
    #     self.assertContains(response, "uio")
    #     self.assertNotContains(response, "xyz")
    #     self.assert_menu(response)

    # def test_sort_books_with_author_asc_by_name(self):
    #     self._create_test_books()
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.books_sort_form_input["sort"] = BooksSortForm.ASC_NAME
    #     target_url = reverse('show_sorted', kwargs={"searched": self.book_author_form_input['searched'], "label": self.book_author_form_input["category"]})
    #     response = self.client.get(target_url,self.books_sort_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form= response.context['form']
    #     self.assertTrue(isinstance(form, BooksSortForm)) 
    #     self.assertTrue(form.is_valid())
    #     self.assertEqual(form.cleaned_data.get('sort'), 'name_asc')
    #     self.assertContains(response, "James")
    #     self.assertNotContains(response, "joe") 
    #     self.assert_menu(response) 

    # def test_sort_books_with_title_asc_by_rating(self):
    #     self._create_test_books()
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.books_sort_form_input["sort"] = BooksSortForm.ASC_RATING
    #     target_url = reverse('show_sorted', kwargs={"searched": self.book_title_form_input['searched'], "label": self.book_title_form_input["category"]})
    #     response = self.client.get(target_url,self.books_sort_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form= response.context['form']
    #     self.assertTrue(isinstance(form, BooksSortForm)) 
    #     self.assertTrue(form.is_valid())
    #     self.assertEqual(form.cleaned_data.get('sort'), 'rating_asc')
    #     self.assert_menu(response) 

    # def test_sort_books_with_title_desc_by_rating(self):
    #     self._create_test_books()
    #     self.client.login(username=self.user.username, password='Password123')
    #     self.books_sort_form_input["sort"] = BooksSortForm.DESC_RATING
    #     target_url = reverse('show_sorted', kwargs={"searched": self.book_title_form_input['searched'], "label": self.book_title_form_input["category"]})
    #     response = self.client.get(target_url,self.books_sort_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form= response.context['form']
    #     self.assertTrue(isinstance(form, BooksSortForm)) 
    #     self.assertTrue(form.is_valid())
    #     self.assertEqual(form.cleaned_data.get('sort'), 'rating_desc')
    #     self.assert_menu(response) 
    
    # def test_post_search_sort_with_empty_str(self):
    #     self.client.login(username=self.user.username, password='Password123')
    #     url = reverse('show_sorted', kwargs={"searched": self.book_author_form_input['searched'], "label": self.book_author_form_input["category"]})
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     self.assertContains(response, "You forgot to search!")
    #     self.assert_menu(response)

    # def test_invalid_form(self):
    #     self._create_test_books()
    #     self.client.login(username=self.user.username, password='Password123')
    #     target_url = reverse('show_sorted', kwargs={"searched": self.book_author_form_input['searched'], "label": self.book_author_form_input["category"]})
    #     response = self.client.get(target_url,self.invalid_form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'search_page.html')
    #     form = response.context['form']
    #     self.assertFalse(form.is_valid())

    def _create_test_books(self, book_count=6):
        isbn_num = ['0425176428', '0060973129','0374157065', '0393045218', '0399135782','034545104X'
                    ,'155061224','446520802', '380000059','380711524']
        
        for book_id in range(book_count):
            Book.objects.create(
                ISBN = isbn_num[book_id],
                title =f'book{book_id} title',
                author = f'book{book_id} author', 
                genre = f'genre {book_id}'
            )


    
