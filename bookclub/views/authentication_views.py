from bookclub.forms import LogInForm
from bookclub.helpers import generate_token
from bookclub.models import User
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import FormView, TemplateView
from system import settings

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to direct to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url'"
            )
        else:
            return self.redirect_when_logged_in_url

class LogInView(LoginProhibitedMixin, FormView):
    """Handle log in attempt."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = 'home'

    def get(self, request):
        """Display log in template."""
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or ''
        user = form.get_user()

        if user and not user.email_verified:
            messages.add_message(request, messages.ERROR,
                'Email is not verified, please check your email inbox!')
            return render(request, 'log_in.html', {'form': form, 'next': self.next, 'request': request, 'user': user})

        if user:
            login(request, user)
            if len(user.books.all()) == 0:
                redirect_url = self.next or 'initial_genres'
            else:
                redirect_url = self.next or 'home'
            return redirect(redirect_url)

        messages.add_message(request, messages.ERROR, 'The credentials provided were invalid!')
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})

"""Handle log out attempt."""
@login_required
def log_out(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, 'You have been logged out!')
    return redirect('welcome')


def send_activiation_email(request, user_id):

    user = get_object_or_404(User, id=user_id)

    if not user.email_verified:
        current_site = get_current_site(request)
        subject = 'Activate your account'
        body = render_to_string('emails/activate.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)}
        )
        email_from = settings.EMAIL_HOST_USER
        email_to = [user.email]

        send_mail(subject, body, email_from, email_to)

        messages.add_message(request, messages.WARNING,
                             'Your email needs verification!')
    else:
        messages.add_message(request, messages.WARNING,
                             'Email is already verified!')

    return redirect('log_in')

class ActivateUserView(TemplateView):
    """Handles activation of a user after their email is verified."""

    template_name = 'activate-fail.html'

    def get(self, *args, **kwargs):
        """Retrieves user if valid and sets its email verified field to true."""
        try:
            uid = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            self.user = User.objects.get(pk=uid)
        except:
            self.user = None

        if self.user and generate_token.check_token(self.user, kwargs['token']):
            self.user.email_verified = True
            self.user.save()
            messages.add_message(self.request, messages.SUCCESS, 'Account verified!')
            return redirect(reverse('log_in'))

        return super().get(*args, **kwargs)
