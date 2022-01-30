from django.urls import reverse
from django.contrib.messages import ERROR, SUCCESS

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