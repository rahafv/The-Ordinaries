from bookclub.forms import SignUpForm, PasswordForm, UserForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.views.generic import FormView, UpdateView
from system import settings
from django.urls import reverse

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

class SignUpView(LoginProhibitedMixin, FormView):
    """Handles user sign up."""

    form_class = SignUpForm
    template_name = 'sign_up.html'
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN
    user = None

    def form_valid(self, form):
        """Saves the user when form is validated."""
        self.user = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        return reverse('send_verification', kwargs={'user_id':self.user.id})

class PasswordView(LoginRequiredMixin, FormView):
    """Handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""
        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""
        messages.add_message(self.request, messages.SUCCESS, 'Password updated!')
        return reverse('home')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = UserForm
    template_name = 'edit_profile.html'
    form_class = UserForm

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to update the date_of_birth of the given user"""
        kwargs = super(ProfileUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(
            self.request, messages.SUCCESS, 'Profile updated!')
        return reverse('profile')