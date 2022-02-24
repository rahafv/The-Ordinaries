from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import LoginRedirectTester, MessageTester 

class ClubDeletionConfirmationTest(TestCase, LoginRedirectTester, MessageTester):

    fixtures=[
        'bookclub/tests/fixtures/other_club.json',
        'bookclub/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(id=3)
        self.club = Club.objects.get(id=2)
        self.url = reverse('delete_club_confirmation', kwargs={'club_id': self.club.id})

    def test_delete_confirmation_url(self):
         self.assertEqual(self.url, f"/confirm_delete_club/{self.club.id}")

    def test_get_delete_confirmation_page_redirects_when_not_logged_in(self):
        self.assert_redirects_when_not_logged_in()

    def test_get_club_delete_confirmation(self):
        self.client.login(username=self.user.username, password='Password123')
        self.url = reverse('delete_club_confirmation', kwargs={'club_id': self.club.id})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_club_confirmation_page.html')

    def test_non_owners_cannot_see_delete_confirmation(self):
        self.non_owner = User.objects.get(id=4)
        self.client.login(username=self.non_owner.username, password='Password123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_page.html")
        self.assert_error_message(response)
    