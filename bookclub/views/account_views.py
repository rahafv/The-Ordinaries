from bookclub.forms import PasswordForm, UserForm
from bookclub.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import FormView, UpdateView
from django.views.generic.base import TemplateView
from system import settings


class PasswordView(LoginRequiredMixin, FormView):
    """Handle password change requests."""

    template_name = 'account_templates/password.html'
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

class ProfilePageView(LoginRequiredMixin, TemplateView):
    """Show user profile page."""
    model = User
    template_name = 'account_templates/profile_page.html'
    pk_url_kwarg = "user_id"

    def get(self, *args, **kwargs):
        """Retrieves the user_id and is_clubs from url and stores it in self for later use."""
        self.user_id = kwargs.get('user_id', None)
        return super().get(self.request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template"""
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User.objects, id=self.request.user.id)

        if self.user_id:
            user = get_object_or_404(User.objects, id=self.user_id)
            
        if self.request.GET.get('filter') == 'Reading list':
            books_queryset = User.objects.get(id=user.id).books.all()
            books_count = books_queryset.count()
            books_pg = Paginator(books_queryset, settings.BOOKS_PER_PAGE)
            page_number = self.request.GET.get('page')
            books = books_pg.get_page(page_number)
            context['items'] = books
            context['items_count'] = books_count
            context['is_clubs'] = False

        if self.request.GET.get('filter') == 'Clubs':
            clubs_queryset = User.objects.get(id=user.id).clubs.all()
            clubs_count = clubs_queryset.count()
            clubs_pg = Paginator(clubs_queryset, settings.CLUBS_PER_PAGE)
            page_number = self.request.GET.get('page')
            clubs = clubs_pg.get_page(page_number)
            context['items'] = clubs
            context['items_count'] = clubs_count
            context['is_clubs'] = True

        context['user'] = user
        context['following'] = self.request.user.is_following(user)
        context['followable'] = (self.request.user != user)

        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update logged-in user's profile."""

    model = UserForm
    template_name = "account_templates/edit_profile.html"
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

