from cProfile import label
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Book
from bookclub.forms import RatingForm
from bookclub.tests.helpers import LoginRedirectTester, MenuTestMixin


class BookDetailsTest(TestCase, LoginRedirectTester , MenuTestMixin):

    fixtures=['bookclub/tests/fixtures/default_book.json',
              'bookclub/tests/fixtures/default_user.json']

    def setUp(self):
        self.target_book = Book.objects.get(ISBN='0195153448')
        self.user = User.objects.get(id=1)
        self.url = reverse('book_details', kwargs={'book_id': self.target_book.id})
       
        self.form_input = {
            'progress-pages': '100',
            'progress-comment-pages':'well written',
        }
        
    def test_book_details_url(self):
        self.assertEqual(self.url,f'/book/{self.target_book.id}/book_details')

    def test_get_book_details_with_valid_ISBN(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')
        self.assert_menu(response)

    def test_get_book_details_with_invalid_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('book_details', kwargs={'book_id': self.target_book.id+99999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404) 

    def test_get_rating_form(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RatingForm))
        self.assertFalse(form.is_bound)



    def test_post_update_progress_form(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')
        user_progress = response.context['user_progress']
        self.assertNotEqual(user_progress,False)
        self.assertDictEqual(user_progress, {'comment':self.form_input['progress-comment-pages'], 'progress':self.form_input['progress-pages'], 'label':"Pages"})
        form = response.context['form']
        self.assertTrue(isinstance(form, RatingForm))
        self.assertFalse(form.is_bound)
    
    def test_post_update_progress_form_with_empty_comment(self):
        self.client.login(username=self.user.username, password="Password123")
        self.form_input['progress-comment-pages']= ''
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')
        user_progress = response.context['user_progress']
        self.assertNotEqual(user_progress,False )
        self.assertDictEqual(user_progress, {'comment':'', 'progress':self.form_input['progress-pages'], 'label':"Pages"})
        form = response.context['form']
        self.assertTrue(isinstance(form, RatingForm))
        self.assertFalse(form.is_bound)


    def test_post_update_progress_form_with_empty_pages(self):
        self.client.login(username=self.user.username, password="Password123")
        self.form_input['progress-pages']=''
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')
        user_progress = response.context['user_progress']
        self.assertEqual(user_progress,False )    
        form = response.context['form']
        self.assertTrue(isinstance(form, RatingForm))
        self.assertFalse(form.is_bound)



    def test_post_update_progress_percentage_form(self):
        form_input_percent = {'progress-percent':'90', 'progress-comment-percent':'well written'}
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, form_input_percent, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')
        user_progress = response.context['user_progress']
        self.assertNotEqual(user_progress,False)
        self.assertDictEqual(user_progress, {'comment':form_input_percent['progress-comment-percent'], 'progress':form_input_percent['progress-percent'], 'label':'Percent'})
        form = response.context['form']
        self.assertTrue(isinstance(form, RatingForm))
        self.assertFalse(form.is_bound)
    
    def test_post_update_progress_percentage_form_with_empty_comment(self):
        form_input_percent = {'progress-percent':'90', 'progress-comment-percent':''}
        self.client.login(username=self.user.username, password="Password123")
        self.form_input['progress-comment-pages']= ''
        response = self.client.post(self.url,form_input_percent, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')
        user_progress = response.context['user_progress']
        self.assertNotEqual(user_progress,False )
        self.assertDictEqual(user_progress, {'comment':form_input_percent['progress-comment-percent'], 'progress':form_input_percent['progress-percent'], 'label':'Percent'})
        form = response.context['form']
        self.assertTrue(isinstance(form, RatingForm))
        self.assertFalse(form.is_bound)


    def test_post_update_progress_percentage_form_with_0_percent(self):
        form_input_percent = {'progress-percent':'0', 'progress-comment-percent':'well written'}
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, form_input_percent, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')
        user_progress = response.context['user_progress']
        self.assertDictEqual(user_progress, {'comment':form_input_percent['progress-comment-percent'], 'progress':form_input_percent['progress-percent'], 'label':'Percent'})
        form = response.context['form']
        self.assertTrue(isinstance(form, RatingForm))
        self.assertFalse(form.is_bound)

    def test_post_update_progress_percentage_form_with_None_percent(self):
        form_input_percent = { 'progress-comment-percent':'well written'}
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, form_input_percent, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_details.html')
        user_progress = response.context['user_progress']
        self.assertEqual(user_progress,False )    
        form = response.context['form']
        self.assertTrue(isinstance(form, RatingForm))
        self.assertFalse(form.is_bound)


    def test_book_details_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_post_book_details_redirects_when_not_logged_in(self):
       self.assert_post_redirects_when_not_logged_in()

    