"""Tests of the book list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Book
from bookclub.forms import BooksSortForm
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin
from system import settings

class BooksListTest(TestCase, LoginRedirectTester,MenuTestMixin):
    """Tests of the book list view."""

    fixtures=['bookclub/tests/fixtures/default_book.json',
                'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.target_book = Book.objects.get(ISBN='0195153448')
        self.user = User.objects.get(id=1)
        self.sec_user = User.objects.get(id=2)

        self.club = Club.objects.get(id=1)
        self.url = reverse('books_list')
        self.BOOKS_PER_PAGE = 15
        self.form_input = {
            'sort':BooksSortForm.DESC_NAME,
        }

    def test_books_list_url(self):
        self.assertEqual(self.url,f'/books/')

    def test_get_non_members_cannot_access_club_books_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('books_list', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'static_templates/404_page.html')

    def test_get_club_books_list(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        self.url = reverse('books_list', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')  
        self.assert_menu(response)

    def test_get_books_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_books(self.BOOKS_PER_PAGE-1)
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        self.assertEqual(len(response.context['books']),self.BOOKS_PER_PAGE)
        for book_id in range(self.BOOKS_PER_PAGE-1):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
            books_url = reverse('books_list')
            self.assertContains(response, books_url)
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')  
        self.assert_menu(response)

    def test_get_user_empty_books_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_books(self.BOOKS_PER_PAGE-1)
        self.url = reverse('books_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        self.assertContains(response, f'The book list is empty! find more book you might like.')
        self.assertContains(response, f'More books')
        books_url = reverse('books_list')
        self.assertContains(response, books_url)
        self.assert_menu(response)

    def test_get_user_filled_books_list_asc_title(self):
        self.form_input['sort'] = BooksSortForm.ASC_NAME
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_books(self.BOOKS_PER_PAGE-1)
        Book.objects.get(id=2).add_reader(self.user)
        Book.objects.get(id=3).add_reader(self.user)
        self.url = reverse('books_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        for book_id in range(2):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_asc')  
        self.assert_menu(response)


    def test_get_user_filled_books_list_desc_title(self):
        self.form_input['sort'] = BooksSortForm.DESC_NAME
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_books(self.BOOKS_PER_PAGE-1)
        Book.objects.get(id=2).add_reader(self.user)
        Book.objects.get(id=3).add_reader(self.user)
        self.url = reverse('books_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/books.html')
        for book_id in range(2):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
        form= response.context['form']
        self.assertTrue(isinstance(form, BooksSortForm)) 
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('sort'), 'name_desc')  
        self.assert_menu(response)


    def _create_test_books(self, book_count=6):
        isbn_num = ['0425176428', '0002005018', '0060973129','0374157065', '0393045218', '0399135782','034545104X'
                    ,'155061224','446520802','052165615X','521795028', '2080674722','3257224281','600570967','038550120X',
                    '342310538', '425115801','449006522','553561618', '055356451X','786013990','786014512','60517794','451192001','609801279',
                    '671537458','679776818','943066433','1570231028','1885408226','747558167','3442437407','033390804X','3596218098','684867621',
                    '451166892','8440682697','034544003X','380000059','380711524']
        ctr = 0
        for book_id in range(book_count):
            Book.objects.create(
                ISBN = isbn_num[ctr],
                title = f'book{book_id} title',
                author = f'book{book_id} author'
            )
            ctr+=1
