"""Tests of the initial book list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User , Book
from bookclub.tests.helpers import LoginRedirectTester


class InitialBookListViewTestCase(TestCase, LoginRedirectTester ):

    fixtures = ['bookclub/tests/fixtures/other_users.json' , 
                'bookclub/tests/fixtures/other_books.json'
    ]

    def setUp(self):
        self.url = reverse('initial_book_list')
        self.user = User.objects.get(id=5)
        self.other_user = User.objects.get(id=3)

    def test_initial_book_list_url(self):
        self.assertEqual(self.url,'/initial_book_list/') 

    # def test_continue_button_enabled(self):
    #      self.client.login(username=self.other_user.username, password='Password123')
           #self.assertTemplateUsed(response, 'initial_book_list.html')
   

    # def test_show_only_first_eight_books(self):
    #      self.client.login(username=self.user.username, password='Password123')
    #      response = self.client.get(self.url)
    #      self.assertTemplateUsed(response, 'initial_book_list.html')
    #      number_of_books = 
    #      self.assertEqual()

    def create_test_books(self, book_count):
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

    def test_display_eight_books_on_page(self):
        self.client.login(username=self.user.username, password='Password123')
        self.create_test_books(8)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'initial_book_list.html')
        self.assertEqual(len(response.context['books']),8)
        for book_id in range(8):
            self.assertContains(response, f'book{book_id} title')
            self.assertContains(response, f'book{book_id} author')
            books_url = reverse('initial_book_list')
            self.assertContains(response, books_url)
    
    def test_initial_book_list_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()



