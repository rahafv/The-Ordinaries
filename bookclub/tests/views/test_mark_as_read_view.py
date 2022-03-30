"""Tests of the mark as read view."""
from django.test import TestCase
from django.urls import reverse
from notifications.signals import notify
from bookclub.models import User, Club
from bookclub.helpers import NotificationHelper

class MarkAsReadViewTestCase(TestCase):
    """Tests of the mark_as_read view."""

    fixtures = ['bookclub/tests/fixtures/default_user.json', 
                'bookclub/tests/fixtures/other_users.json', 
                'bookclub/tests/fixtures/default_club.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.sec_user = User.objects.get(id=2)
        self.third_user = User.objects.get(id=3)
        self.club=Club.objects.get(id=1)
        self.notificationHelper = NotificationHelper()
        notify.send(self.sec_user, recipient=self.user, verb=self.notificationHelper.NotificationMessages.FOLLOW)
        self.slug = self.user.notifications.unread()[0].slug
        self.url = reverse('mark_as_read', kwargs={'slug': self.slug})
        

    def test_notification_is_read(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = self.user.notifications.unread().count()
        self.assertEqual(self.user.notifications.unread()[0].verb,self.notificationHelper.NotificationMessages.FOLLOW)
        response = self.client.get(self.url, follow=True)
        after_count = self.user.notifications.unread().count()
        self.assertEqual(after_count, before_count - 1)
        redirect_url = reverse('profile', kwargs={'user_id':2} )
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_appropriate_redirect_APPLY(self): 
        self.client.login(username=self.user.username, password="Password123")
        notify.send(self.user, recipient=self.user, verb=self.notificationHelper.NotificationMessages.APPLIED, action_object=self.club, description='notification')
        slug2 = self.user.notifications.unread()[0].slug
        url = reverse('mark_as_read', kwargs={'slug': slug2})
        response = self.client.get(url, follow=True)
        response_url = reverse('applicants_list', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)


    def test_get_appropriate_redirect_ACCEPT(self): 
        self.client.login(username=self.user.username, password="Password123")
        notify.send(self.user, recipient=self.user, verb=self.notificationHelper.NotificationMessages.ACCEPT, action_object=self.club, description='notification')
        slug2 = self.user.notifications.unread()[0].slug
        url = reverse('mark_as_read', kwargs={'slug': slug2})
        response = self.client.get(url, follow=True)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)


    def test_get_appropriate_redirect_REJECT(self): 
        self.client.login(username=self.user.username, password="Password123")
        notify.send(self.user, recipient=self.user, verb=self.notificationHelper.NotificationMessages.REJECT, action_object=self.club, description='notification')
        slug2 = self.user.notifications.unread()[0].slug
        url = reverse('mark_as_read', kwargs={'slug': slug2})
        response = self.client.get(url, follow=True)
        response_url = reverse('club_page', kwargs={'club_id': self.club.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)


    def test_get_appropriate_redirect_FOLLOW(self): 
        self.client.login(username=self.user.username, password="Password123")
        notify.send(self.user, recipient=self.user, verb=self.notificationHelper.NotificationMessages.FOLLOW, action_object=self.club, description='notification')
        slug2 = self.user.notifications.unread()[0].slug
        url = reverse('mark_as_read', kwargs={'slug': slug2})
        response = self.client.get(url, follow=True)
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_appropriate_redirect_wrong_verb(self): 
        self.client.login(username=self.user.username, password="Password123")
        notify.send(self.user, recipient=self.user, verb="test_verb", action_object=self.club, description='notification')
        slug2 = self.user.notifications.unread()[0].slug
        url = reverse('mark_as_read', kwargs={'slug': slug2})
        response = self.client.get(url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)


    


    
