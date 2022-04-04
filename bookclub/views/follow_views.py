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
from django.core.paginator import Paginator

class FollowListView(LoginRequiredMixin, ListView):
    """Display following list of a user."""
    model = User
    template_name = "follow_templates/follow_list.html"
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieve the user_id from url and store it in self for later use."""
        self.user_id = kwargs.get("user_id")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Return following list of a user."""
        self.user = get_object_or_404(User, id=self.user_id)
        followers = self.user.followers.all()
        followees = self.user.followees.all()
        self.is_following = False
        if self.request.GET.get('filter') == 'followers' and followers: 
            return followers
        if self.request.GET.get('filter') == 'following' and followees: 
            self.is_following = True
            return followees
        return []

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['follow_list'] = context["page_obj"]
        context['user'] = self.user
        context['is_following'] = self.is_following
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

