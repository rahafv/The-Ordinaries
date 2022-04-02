from bookclub.forms import PasswordForm, UserForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, UpdateView
from django.urls import reverse

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
    template_name = "edit_profile.html"
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
            self.request, messages.SUCCESS, "Profile updated!")
        return reverse('profile')

