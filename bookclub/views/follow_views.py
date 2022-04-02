from bookclub.models import User
from bookclub.helpers import NotificationHelper
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from notifications.signals import notify
from system import settings

class FollowingListView(LoginRequiredMixin, ListView):
    """Display following list of a user."""

    model = User
    template_name = "follow_list.html"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieves the user_id from url and stores it in self for later use."""
        self.user_id = kwargs.get("user_id")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Returns following list of a user."""
        self.user = get_object_or_404(User, id=self.user_id)
        return self.user.followees.all()

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['follow_list'] = context["page_obj"]
        context['user'] =self.user
        context['is_following'] = True
        context['current_user'] = self.request.user
        return context


class FollowersListView(LoginRequiredMixin, ListView):
    """Displays followers list of a user."""

    model = User
    template_name = "follow_list.html"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieves the user_id from url and stores it in self for later use."""
        self.user_id = kwargs.get("user_id")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Returns followers list of a user."""
        self.user = get_object_or_404(User, id=self.user_id)
        return self.user.followers.all()

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['follow_list'] = context["page_obj"]
        context['user'] = self.user
        context['is_following'] = False
        context['current_user'] = self.request.user
        return context

"""Enable user to follow and unfollow other users."""
@login_required
def follow_toggle(request, user_id):
    current_user = request.user
    followee = get_object_or_404(User.objects, id=user_id)
    notificationHelper = NotificationHelper()

    if(not current_user.is_following(followee)):
        notificationHelper.delete_notifications(current_user, [followee], notificationHelper.NotificationMessages.FOLLOW )
        notify.send(current_user, recipient=followee, verb=notificationHelper.NotificationMessages.FOLLOW,  description='notification' )
    else:

        notificationHelper.delete_notifications(current_user, [followee], notificationHelper.NotificationMessages.FOLLOW )
    current_user.toggle_follow(followee)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))

