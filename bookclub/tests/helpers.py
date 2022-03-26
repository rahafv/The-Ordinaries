from logging import WARNING
from django.urls import reverse
from django.contrib.messages import ERROR, SUCCESS
from with_asserts.mixin import AssertHTMLMixin
from notifications.signals import notify

def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url

class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

class LoginRedirectTester:
    def assert_redirects_when_not_logged_in(self):
        target_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response, target_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")

    def assert_post_redirects_when_not_logged_in(self):
        target_url = reverse_with_next("log_in", self.url)
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertRedirects(
            response, target_url, status_code=302, target_status_code=200
        )
        self.assertTemplateUsed(response, "log_in.html")

class MessageTester:
    def assert_error_message(self, response):
        messages = tuple(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, ERROR)

    def assert_success_message(self, response):
        messages = tuple(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, SUCCESS)

    def assert_warning_message(self, response):
        messages = tuple(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, WARNING)

    def assert_no_message(self, response):
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0) 

class MenuTestMixin(AssertHTMLMixin):
    menu_urls = [
      reverse('password') ,
      reverse('profile') ,
      reverse('books_list') , 
      reverse('clubs_list'),
      reverse('log_out')
      ]

    def assert_menu(self,response):
        for url in self.menu_urls:
            with self.assertHTML(response , f'a[href="{url}"]'):
                pass

    def assert_no_menu(self , response):
        for url in self.menu_urls:
            self.assertNotHTML(response , f'a[href="{url}"]')

class NotificationsTester(): 
    def sendNotification(self, userActor, receptient_user, clubActor): 
        notify.send(userActor, recipient=receptient_user, verb= "test user", description='user-event')      
        notify.send(clubActor, recipient=receptient_user, verb= "test club", action_object=userActor, description='club-event-U' )
