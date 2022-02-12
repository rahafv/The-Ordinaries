from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import reverse_with_next
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenueTestMixin
from system import settings

class MembersListTest(TestCase, LoginRedirectTester, MessageTester,MenueTestMixin):

    fixtures=[
                'bookclub/tests/fixtures/default_club.json',
                'bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(id=3)
        self.club = Club.objects.get(id=1)
        self.url = reverse('members_list', kwargs={'club_id': self.club.id})

    def test_user_list_url(self):
         self.assertEqual(self.url, f"/club/{self.club.id}/members/")

    def test_get_members_page_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_get_club_members_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('members_list', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assert_menu(response)

    def test_get_members_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_members(settings.MEMBERS_PER_PAGE-1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertEqual(len(response.context['members']), settings.MEMBERS_PER_PAGE)
        for user_id in range(settings.MEMBERS_PER_PAGE-1):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id} Last{user_id}')

        for member in self.club.members.all():
            if member.id != self.user.id:
                member_profile_url = reverse('profile', kwargs={'club_id': self.club.id, 'user_id': member.id })
                self.assertContains(response, member_profile_url)
        self.assert_menu(response)
    
    def test_get_members_list_with_pagination(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_members(settings.MEMBERS_PER_PAGE*2+3)
        response = self.client.get(self.url)
        self.assert_menu(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertEqual(len(response.context['members']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['members']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_one_url = reverse('members_list', kwargs={'club_id': self.club.id}) + '?page=1'
        response = self.client.get(page_one_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertEqual(len(response.context['members']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['members']
        self.assertFalse(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_two_url = reverse('members_list', kwargs={'club_id': self.club.id}) + '?page=2'
        response = self.client.get(page_two_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertEqual(len(response.context['members']), settings.MEMBERS_PER_PAGE)
        page_obj = response.context['members']
        self.assertTrue(page_obj.has_previous())
        self.assertTrue(page_obj.has_next())
        page_three_url = reverse('members_list', kwargs={'club_id': self.club.id}) + '?page=3'
        response = self.client.get(page_three_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members_list.html')
        self.assertEqual(len(response.context['members']), 5)
        page_obj = response.context['members']
        self.assertTrue(page_obj.has_previous())
        self.assertFalse(page_obj.has_next())
        self.assert_menu(response)

    def test_non_members_cannot_see_members_list(self):
        self.non_member = User.objects.get(id=4)
        self.client.login(username=self.non_member.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_page.html")
        self.assert_error_message(response)
        self.assert_menu(response)
    

    def _create_test_members(self, members_count=10):
        for user_id in range(members_count):
            user = User.objects.create_user(f'@user{user_id}',
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
            )
            self.club.add_member(user)