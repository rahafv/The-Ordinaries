"""Test suite for the post progress view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.tests.helpers import LoginRedirectTester, MenuTestMixin, MessageTester


class PostProgressTest(TestCase, LoginRedirectTester ,MessageTester, MenuTestMixin):
    """Test suite for the post progress view."""

    fixtures=['bookclub/tests/fixtures/default_book.json',
              'bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.target_book = Book.objects.get(ISBN='0195153448')
        self.user = User.objects.get(id=1)
        self.url = reverse('post_progress', kwargs={'book_id': self.target_book.id})
       
        self.form_input = {
            'progress': '100',
            'comment':'well written',
        }
        
    def test_book_progress_url(self):
        self.assertEqual(self.url,f'/book/{self.target_book.id}/post_progress')
    
    def test_get_book_with_valid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('post_progress', kwargs={'book_id': self.target_book.id})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200) 

    def test_get_book_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('post_progress', kwargs={'book_id': self.target_book.id+99999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404) 

    def test_post_update_progress_form(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/book_details.html')
        self.assert_success_message(response)
    
    def test_post_update_progress_form_with_empty_comment(self):
        self.form_input['comment'] = ""
        self.client.login(username=self.user.username, password="Password123")
        self.form_input['progress-comment-pages']= ''
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/book_details.html')
        self.assert_success_message(response)

    def test_post_update_progress_form_with_empty_pages(self):
        self.client.login(username=self.user.username, password="Password123")
        self.form_input['progress']=''
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_templates/book_details.html')
        self.assert_error_message(response)


    def test_get_book_progress_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_post_book_progress_redirects_when_not_logged_in(self):
       self.assert_post_redirects_when_not_logged_in()

    