from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import reverse_with_next

class ShowUserTest(TestCase):

    fixtures = [
        'bookclub/tests/fixtures/default_user.json',
        'bookclub/tests/fixtures/other_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.followee = User.objects.get(id=2)
        self.url = reverse('follow_toggle', kwargs={'user_id': self.followee.id})

    def test_follow_toggle_url(self):
        self.assertEqual(self.url,f'/follow_toggle/{self.followee.id}/')

    def test_get_follow_toggle_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)

    def test_get_follow_toggle_for_followee(self):
        self.client.login(username=self.user.username, password='Password123')
        self.user.toggle_follow(self.followee)
        user_followers_before = self.user.follower_count()
        followee_followers_before = self.followee.follower_count()
        response = self.client.get(self.url, follow=True)
        user_followers_after = self.user.follower_count()
        followee_followers_after = self.followee.follower_count()
        self.assertEqual(user_followers_before, user_followers_after)
        self.assertEqual(followee_followers_before, followee_followers_after+1)
        response_url = reverse('profile', kwargs={'user_id': self.followee.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile_page.html')
       

    def test_get_follow_toggle_for_non_followee(self):
        self.client.login(username=self.user.username, password='Password123')
        user_followers_before = self.user.follower_count()
        followee_followers_before = self.followee.follower_count()
        response = self.client.get(self.url, follow=True)
        user_followers_after = self.user.follower_count()
        followee_followers_after = self.followee.follower_count()
        self.assertEqual(user_followers_before, user_followers_after)
        self.assertEqual(followee_followers_before+1, followee_followers_after)
        response_url = reverse('profile', kwargs={'user_id': self.followee.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile_page.html')

   
    def test_get_follow_toggle_with_invalid_user_id(self):
        self.client.login(username=self.user.username, password='Password123')
        url = reverse('follow_toggle', kwargs={'user_id': self.user.id+9999})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404) 
