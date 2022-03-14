from django.test import TestCase
from django.urls import reverse
from bookclub.models import Meeting, User, Book
from bookclub.tests.helpers import LoginRedirectTester , MenuTestMixin

class SearchPageViewTest(TestCase, LoginRedirectTester, MenuTestMixin):

    fixtures=['bookclub/tests/fixtures/default_user.json', 
        'bookclub/tests/fixtures/other_users.json', 
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/default_book.json',
        'bookclub/tests/fixtures/default_meeting.json', 
        'bookclub/tests/fixtures/other_meeting.json']  

    def setUp(self):
        self.meeting = Meeting.objects.get(id=3)
        self.sec_meeting = Meeting.objects.get(id=1)
        self.url = reverse('search_book', kwargs={ 'meeting_id':self.meeting.id})
        self.sec_url = reverse('search_book', kwargs={ 'meeting_id':self.sec_meeting.id})
        self.user = User.objects.get(id=2)
        self.sec_user = User.objects.get(id=1)
        self.BOOKS_PER_PAGE = 15

        self.book_title_form_input = {
            'searched':'uio',
        }

        self.empty_form_input = {
            'searched':'',
        }

    def test_search_book_url(self):
        self.assertEqual(self.url, f'/meeting/{self.meeting.id}/search/')

    def test_cant_access_when_book(self):
        self.client.login(username=self.sec_user.username, password='Password123')
        response = self.client.get(self.sec_url)
        response_url = reverse('choice_book_list', kwargs={'meeting_id': self.sec_meeting.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=404)

    def test_cant_access_when_not_chooser(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.sec_url)
        response_url = reverse('choice_book_list', kwargs={'meeting_id': self.sec_meeting.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=404)

    def test_search_books_with_title(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_books()
        response = self.client.get(self.url, self.book_title_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'choice_book_list.html')
        self.assertContains(response, "uio")
        self.assertNotContains(response, "xyz")
        self.assert_menu(response)

    def test_search_with_empty_str(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url, self.empty_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'choice_book_list.html')
        self.assertContains(response, "You forgot to search!")
        self.assert_menu(response)

    def test_choice_book_list_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

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
            else: 
                title = 'xyz'
                author = 'joe'

            Book.objects.create(
                ISBN = isbn_num[book_id],
                title =title,
                author = author, 
            )


    
