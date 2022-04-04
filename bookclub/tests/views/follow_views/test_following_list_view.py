"""Test suite for the followings list view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User 
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenuTestMixin
from system import settings

class FollowingsListTest(TestCase, LoginRedirectTester, MessageTester, MenuTestMixin):
    """Test suite for the followings list view."""

    fixtures=[
                'bookclub/tests/fixtures/default_user.json',
                'bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.other_user = User.objects.get(id=1)
        self.url = reverse('following_list', kwargs={'user_id': self.user.id})

    def test_user_list_url(self):
         self.assertEqual(self.url, f"/{self.user.id}/followings/")

    def test_get_members_page_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_get_user_following_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('following_list', kwargs={'user_id': self.user.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'follow_templates/follow_list.html')
        self.assert_menu(response)

    def test_get_followings_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_followings(settings.MEMBERS_PER_PAGE)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'follow_templates/follow_list.html')
        self.assertEqual(len(response.context['follow_list']), settings.MEMBERS_PER_PAGE)
        for user_id in range(settings.MEMBERS_PER_PAGE-1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id} Last{user_id}')

        for user in self.user.followees.all():
            if user.id != self.user.id:
                member_profile_url = reverse('profile', kwargs={ 'user_id': user.id })
                self.assertContains(response, member_profile_url)
        self.assert_menu(response)
    
    def test_get_followings_list_with_pagination(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_followings(settings.MEMBERS_PER_PAGE*2+3)
        response = self.client.get(self.url)
        self.assert_menu(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'follow_templates/follow_list.html')
        self.assertEqual(len(response.context['follow_list']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['follow_list']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('following_list', kwargs={'user_id': self.user.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'follow_templates/follow_list.html')
        self.assertEqual(len(response.context['follow_list']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['follow_list']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('following_list', kwargs={'user_id': self.user.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'follow_templates/follow_list.html')
        self.assertEqual(len(response.context['follow_list']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['follow_list']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('following_list', kwargs={'user_id': self.user.id}) + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'follow_templates/follow_list.html')
        self.assertEqual(len(response.context['follow_list']), 3)
        page_obj = response.context['follow_list']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
        self.assert_menu(response)

    def _create_test_followings(self, user_count=10):
        for user_id in range(user_count):
            user = User.objects.create_user(f'@user{user_id}',
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
            )
            self.user._follow(user)