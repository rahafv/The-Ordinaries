"""Tests of the mark as read view."""
from django.test import TestCase
from django.urls import reverse
from notifications.signals import notify
from bookclub.models import User


class MarkAsReadViewTestCase(TestCase):
    """Tests of the mark_as_read view."""

    fixtures = ['bookclub/tests/fixtures/default_user.json' , 
                'bookclub/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.sec_user = User.objects.get(id=2)
        notify.send(self.sec_user, recipient=self.user, verb="followed you")
        self.slug = self.user.notifications.unread()[0].slug
        self.url = reverse('mark_as_read', kwargs={'slug': self.slug})
        

    def test_notification_is_read(self):
        self.client.login(username=self.user.username, password='Password123')
        before_count = self.user.notifications.unread().count()
        self.assertEqual(self.user.notifications.unread()[0].verb,"followed you")
        response = self.client.get(self.url, follow=True)
        after_count = self.user.notifications.unread().count()
        self.assertEqual(after_count, before_count - 1)
        redirect_url = reverse('profile', kwargs={'user_id':2} )
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)