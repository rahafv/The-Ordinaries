"""Tests of the initial book list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User , Book
from bookclub.tests.helpers import LoginRedirectTester


class InitialBookListViewTestCase(TestCase, LoginRedirectTester ):

    fixtures = ['bookclub/tests/fixtures/default_user.json']  
   
    def setUp(self):
        self.url = reverse('initial_book_list')
        self.user = User.objects.get(id=1)

    def test_initial_book_list_url(self):
        self.assertEqual(self.url,'/initial_book_list/') 

    def create_test_books(self, book_count=10):
        isbn_num = ['0425176428', '0060973129','0374157065', '0393045218', '0399135782','034545104X'
                    ,'155061224','446520802', '380000059','380711524']
        ctr = 0
        for book_id in range(book_count):
            Book.objects.create(
                ISBN = isbn_num[ctr],
                title = f'book{book_id} title',
                author = f'book{book_id} author'
            )
            ctr+=1

    def test_display_only_eight_books_on_page(self):
        self.client.login(username=self.user.username, password='Password123')
        self.create_test_books(10)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'initial_book_list.html')
        self.assertEqual(len(response.context['my_books']),8)
        for book_id in range(8):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
        books_url = reverse('initial_book_list')
        self.assertContains(response, books_url)
    
    def test_initial_book_list_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()



