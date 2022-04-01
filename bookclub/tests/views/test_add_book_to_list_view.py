from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import LoginRedirectTester, MenuTestMixin, MessageTester

class AddBookToListViewTestCase(TestCase, LoginRedirectTester, MenuTestMixin, MessageTester):
    
    fixtures = ['bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/other_users.json',
                'bookclub/tests/fixtures/default_book.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.book = Book.objects.get(ISBN='0195153448')
        self.url = reverse('add_book_to_list', kwargs={'book_id': self.book.id})
        self.follower = User.objects.get(username = "willsmith")
        self.follower.toggle_follow(self.user)

    def test_book_details_url(self):
        self.assertEqual(self.url,f'/book/{self.book.id}/add_to_list')

    def test_successful_book_addition(self):
        count = self.book.readers_count
        events_before_count = self.follower.notifications.unread().count()
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_books()
        target_url = reverse("book_details", kwargs={"book_id": self.book.id})
        response = self.client.get(self.url, HTTP_REFERER=target_url, follow=True)
        self.assertTemplateUsed(response, 'book_details.html')
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
        self.assert_menu(response)
        self.book.refresh_from_db()
        self.assertEqual(self.book.readers_count, count+1)
        self.assertEqual(events_before_count + 1, self.follower.notifications.unread().count())
        self.assertContains(response, 'You might also like..')
        self.assertEqual(len(response.context['recs']),6)

    def test_successful_book_removal(self):
        self.client.login(username=self.user.username, password='Password123')
        self.book.add_reader(self.user)
        self.book.refresh_from_db()
        count = self.book.readers_count
        target_url = reverse("book_details", kwargs={"book_id": self.book.id})
        response = self.client.get(self.url, HTTP_REFERER=target_url, follow=True)
        self.assertTemplateUsed(response, 'book_details.html')
        self.assertRedirects(response, target_url, status_code=302, target_status_code=200)
        self.assert_success_message(response)
        self.assert_menu(response)
        self.book.refresh_from_db()
        self.assertEqual(self.book.readers_count, count-1)


    def test_add_to_list_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def _create_test_books(self, book_count=7):
        isbn_num = [ '425115801','449006522','553561618', '055356451X','786013990','786014512','60517794','451192001','609801279',
                    '671537458','679776818','943066433','1570231028','1885408226','747558167','3442437407','033390804X','3596218098','684867621',
                    '451166892','8440682697','034544003X','380000059','380711524']
        ctr = 0
        for book_id in range(book_count):
            genre = "Classics,European Literature,Czech Literature"
            if ctr == 0:
                genre = ""

            Book.objects.create(
                ISBN = isbn_num[ctr],
                title = f'book{book_id} title',
                author = f'book{book_id} author',
                genre = genre
            )
            ctr+=1