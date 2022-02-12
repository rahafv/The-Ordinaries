from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import reverse_with_next
from bookclub.tests.helpers import LoginRedirectTester, MessageTester , MenueTestMixin
from bookclub.views import accept_applicant

class MembersListTest(TestCase, LoginRedirectTester, MessageTester,MenueTestMixin):

    fixtures=[
        'bookclub/tests/fixtures/default_club.json',
        'bookclub/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(id=3)
        self.club = Club.objects.get(id=1)
        self.club.club_type = Club.ClubType.PRIVATE
        self.url = reverse('applicants_list', kwargs={'club_id': self.club.id})

    def test_applicants_list_url(self):
         self.assertEqual(self.url, f"/club/{self.club.id}/applicants/")

    def test_get_applicants_page_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_get_club_applicants_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('applicants_list', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assert_menu(response)

    def test_get_applicants_list(self):
        self.client.login(username=self.user.username, password='Password123')
        self._create_test_applicants(15)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'applicants_list.html')
        self.assertEqual(len(response.context['applicants']), 15)
        members_count = self.club.member_count
        for user_id in range(15):
            self.assertContains(response, f'user{user_id}')
            self.assertContains(response, f'First{user_id} Last{user_id}')

        for applicant in self.club.applicants.all():
            if applicant.id != self.user.id:
                applicant_profile_url = reverse('profile', kwargs={'club_id': self.club.id, 'user_id': applicant.id })
                self.assertContains(response, applicant_profile_url)
        
        for applicant in self.club.applicants.all():
            if applicant.id != self.user.id:
                accept_applicant = reverse('accept_applicant', kwargs={'club_id': self.club.id, 'user_id': applicant.id })
                self.assertContains(response, accept_applicant)
        
        for applicant in self.club.applicants.all():
            if applicant.id != self.user.id:
                reject_applicant = reverse('reject_applicant', kwargs={'club_id': self.club.id, 'user_id': applicant.id })
                self.assertContains(response, reject_applicant)

        self.assert_menu(response)

    def test_non_owners_cannot_see_applicants_list(self):
        self.non_owner = User.objects.get(id=4)
        self.client.login(username=self.non_owner.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_page.html")
        self.assert_error_message(response)
        self.assert_menu(response)
    

    def _create_test_applicants(self, applicants_count=10):
        for user_id in range(applicants_count):
            user = User.objects.create_user(f'@user{user_id}',
                email=f'user{user_id}@test.org',
                password='Password123',
                first_name=f'First{user_id}',
                last_name=f'Last{user_id}',
                bio=f'Bio {user_id}',
            )
            self.club.add_applicant(user)