from bookclub.forms import ClubsSortForm, CreateClubForm, TransferOwnershipForm, UsersSortForm
from bookclub.helpers import NotificationHelper, SortHelper
from bookclub.models import Club, User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, FormView, UpdateView
from notifications.signals import notify
from system import settings


class CreateClubView(LoginRequiredMixin, CreateView):
    """Handle creation of new club."""

    model = Club
    template_name = 'create_club.html'
    form_class = CreateClubForm

    def form_valid(self, form):
        """Process a valid form."""
        club_owner = self.request.user
        form.instance.owner = club_owner
        self.club = form.save()
        notify.send(club_owner, recipient=club_owner.followers.all(), verb=NotificationHelper().NotificationMessages.CREATE, action_object=self.club, description='user-event-C' )
        self.club.add_member(club_owner)
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        return reverse('club_page', kwargs={"club_id": self.club.id})

    def handle_no_permission(self):
        """If there is no permission, redirect to log in."""
        return redirect(reverse('log_in') + '?next=/create_club/')


class ClubPageView(LoginRequiredMixin, DetailView):
    """Show individual club details."""

    model = Club
    template_name = 'club_page.html'
    pk_url_kwarg = 'club_id'
    context_object_name = 'club'

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data()
        user = self.request.user

        context['is_member'] = context['club'].is_member(user)
        context['is_applicant'] = context['club'].is_applicant(user)
        upcoming_meetings = context['club'].get_upcoming_meetings()
        try:
            context['upcoming_meeting'] = upcoming_meetings[0]
        except:
            context['upcoming_meeting']=None

        return context


class ClubsListView(LoginRequiredMixin, ListView):
    """Display list of clubs."""

    model = Club
    template_name = "clubs.html"
    paginate_by = settings.CLUBS_PER_PAGE


    def get(self, request, *args, **kwargs):
        """Retrieves the user_id from url (if exists) and stores it in self for later use."""
        self.user_id = kwargs.get("user_id")
        self.privacy = self.request.GET.get('privacy')
        self.ownership = self.request.GET.get('ownership')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """If user_id is provided return all clubs the user is a member in, else return all clubs."""
        self.general = True
        self.clubs_queryset = super().get_queryset()
        self.user = self.request.user

        if self.user_id:
            self.user = User.objects.get(id=self.user_id)
            self.clubs_queryset = self.user.clubs.all()
            self.general = False

        self.form = ClubsSortForm(self.request.GET or None)

        if self.form.is_valid():
            sort = self.form.cleaned_data.get('sort')
            sort_helper = SortHelper(sort, self.clubs_queryset)
            self.clubs_queryset = sort_helper.sort_clubs()

        self.filtered = False
        if self.privacy == 'public':
            self.clubs_queryset = self.clubs_queryset.filter(club_type='Public')
            self.filtered = True
        elif self.privacy == 'private':
            self.clubs_queryset = self.clubs_queryset.filter(club_type='Private')
            self.filtered = True

        if self.ownership == 'owned':
            self.clubs_queryset = self.clubs_queryset.filter(owner=self.user)
            self.filtered = True

        return self.clubs_queryset

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""

        context = super().get_context_data(**kwargs)
        context['general'] = self.general
        context['privacy'] = self.privacy
        context['ownership'] = self.ownership
        context['filtered'] = self.filtered
        context['form'] = self.form
        context['clubs'] = context["page_obj"]
        context['count'] = self.object_list.count()

        return context


class MembersListView(LoginRequiredMixin, ListView):
    """Display list of members."""

    model = User
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieves the club_id from url and stores it in self for later use."""
        self.club_id = kwargs.get("club_id")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Return all members of a club if the user has access, else return an empty queryset."""
        self.club = get_object_or_404(Club, id=self.club_id)
        self.form = UsersSortForm(self.request.GET or None)
        if(self.club.is_member(self.request.user)):
            self.members_queryset = self.club.members.all()
            if self.form.is_valid():
                sort = self.form.cleaned_data.get('sort')
                sort_helper = SortHelper(sort, self.members_queryset)
                self.members_queryset = sort_helper.sort_users()

            return self.members_queryset
        return self.model.objects.none()

    def get_template_names(self):
        """Returns a different template name if the user does not have access rights."""
        if self.club.is_member(self.request.user):
            return ['members_list.html']
        else:
            messages.add_message(self.request, messages.ERROR, "You cannot access the members list!" )
            return ['club_page.html']

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['members'] = context["page_obj"]
        context['club'] = self.club
        context['current_user'] = self.request.user
        context['form'] = self.form
        return context

"""Enable user to join a club."""
@login_required
def join_club(request, club_id):

    club = get_object_or_404(Club.objects, id=club_id)
    user = request.user
    notificationHelper = NotificationHelper()

    if club.is_member(user):
        messages.add_message(request, messages.ERROR,
                             "Already a member of this club!")
        return redirect('club_page', club_id)

    if club.club_type == "Private":
        if not club.is_applicant(user):
            club.applicants.add(user)
            notify.send(user, recipient=club.owner, verb=notificationHelper.NotificationMessages.APPLIED, action_object=club,  description='notification' )
            messages.add_message(request, messages.SUCCESS,
                                 "You have successfully applied!")
            return redirect('club_page', club_id)
        else:
            messages.add_message(request, messages.ERROR,
                                 "Already applied, awaiting approval!")
            return redirect('club_page', club_id)

    club.members.add(user)
    notificationHelper.delete_notifications(user, user.followers.all(), notificationHelper.NotificationMessages.JOIN, club )
    notify.send(user, recipient=user.followers.all(), verb=notificationHelper.NotificationMessages.JOIN, action_object=club, description='user-event-C' )

    messages.add_message(request, messages.SUCCESS, "Joined club!")
    return redirect('club_page', club_id)


"""Enable a user to withdraw from a club."""
@login_required
def withdraw_club(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    user = request.user

    if user == club.owner:
        messages.add_message(request, messages.ERROR,
                             "Ownership must be transferred before withdrawing from club!")
        return redirect('club_page', club_id)

    if not club.is_member(user):
        messages.add_message(request, messages.ERROR,
                             "You are not a member of this club!")
        return redirect('club_page', club_id)

    club.members.remove(user)
    notificationHelper = NotificationHelper()
    notificationHelper.delete_notifications(user, user.followers.all(), notificationHelper.NotificationMessages.WITHDRAW, club )
    notify.send(user, recipient=user.followers.all(), verb=notificationHelper.NotificationMessages.WITHDRAW, action_object=club, description='user-event-C' )

    messages.add_message(request, messages.SUCCESS, "Withdrew from club!")
    return redirect('club_page', club_id)

class ApplicantsListView(LoginRequiredMixin, ListView):
    """Displays applicants list of a club."""

    model = User
    template_name = "applicants_list.html"
    context_object_name = "applicants"

    def get(self, request, *args, **kwargs):
        """Retrieves the club_id from url and stores it in self for later use."""
        self.club_id = kwargs.get("club_id")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Return all applicants of a club if the user is owner, else return an empty queryset."""
        self.club = get_object_or_404(Club, id=self.club_id)
        self.form = UsersSortForm(self.request.GET or None)
        if(self.club.owner == self.request.user):
            self.applicants_queryset = self.club.applicants.all()
            if self.form.is_valid():
                sort = self.form.cleaned_data.get('sort')
                sort_helper = SortHelper(sort, self.applicants_queryset)
                self.applicants_queryset = sort_helper.sort_users()

            return self.applicants_queryset
        return self.model.objects.none()

    def get_template_names(self):
        """Returns a different template name if the user is not owner."""
        if self.club.owner == self.request.user:
            return ['applicants_list.html']
        else:
            messages.add_message(self.request, messages.ERROR, "You cannot access the applicants list!" )
            return ['club_page.html']

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        context['club'] = self.club
        context['current_user'] = self.request.user
        context['form'] = self.form
        return context

@login_required
def accept_applicant(request, club_id, user_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    applicant = get_object_or_404(User.objects, id=user_id)
    if(current_user == club.owner):
        club.members.add(applicant)
        club.applicants.remove(applicant)
        notify.send(applicant, recipient=applicant.followers.all(), verb=NotificationHelper().NotificationMessages.JOIN, action_object=club, description='user-event-C' )
        messages.add_message(request, messages.SUCCESS, "Applicant accepted!")
        notify.send(current_user, recipient=applicant, verb= NotificationHelper().NotificationMessages.ACCEPT, action_object=club, description='notification' )
        return redirect('applicants_list', club_id)
    else:
        messages.add_message(request, messages.ERROR,
                             "You cannot change applicant's status!")
        return redirect('club_page', club_id)


@login_required
def reject_applicant(request, club_id, user_id):
    current_user = request.user
    club = get_object_or_404(Club.objects, id=club_id)
    applicant = get_object_or_404(User.objects, id=user_id)
    if(current_user == club.owner):
        club.applicants.remove(applicant)
        messages.add_message(request, messages.WARNING, "Applicant rejected!")
        notify.send(current_user, recipient=applicant, verb=NotificationHelper().NotificationMessages.REJECT, action_object=club,  description='notification')
        return redirect('applicants_list', club_id)
    else:
        messages.add_message(request, messages.ERROR,
                             "You cannot change applicant's status!")
        return redirect('club_page', club_id)

class TransferClubOwnershipView(LoginRequiredMixin, FormView, SingleObjectMixin):
    """Enables owner to transfer ownership to another member."""

    template_name = "transfer_ownership.html"
    form_class = TransferOwnershipForm
    pk_url_kwarg = "club_id"
    context_object_name = "club"
    model = Club

    def get_form_kwargs(self):
        """Generates data that the form needs to initialise."""
        kwargs = super().get_form_kwargs()
        kwargs["club_id"] = self.get_object().id
        kwargs["user_id"] = self.request.user.id
        return kwargs

    def get_context_data(self, **kwargs):
        """Set self.object to store club."""
        self.object = self.get_object()
        return super().get_context_data(**kwargs)

    def get(self, *args, **kwargs):
        """Get method with additonal checks for permissions."""
        club = self.get_object()
        if self.request.user != club.owner:
            messages.add_message(self.request, messages.ERROR, "You are not permitted to access this page!")
            return redirect('club_page', club_id = club.id)

        members = club.members.all().exclude(id=self.request.user.id)
        if members.count() == 0:
            messages.add_message(self.request, messages.WARNING, "There are no other members to tranfer the club to!")
            return redirect('club_page', club_id = club.id)

        return super().get(*args, **kwargs)

    def form_valid(self, form):
        """Changes the owner after the form is validated."""
        self.club = self.get_object()
        member = form.cleaned_data.get("new_owner")
        self.club.make_owner(member)
        notify.send(self.club, recipient=self.club.members.all(), verb=NotificationHelper().NotificationMessages.TRANSFER, action_object=member, description='club-event-U' )

        current_site = get_current_site(self.request)
        subject = self.club.name + ' Club updates'
        email_from = settings.EMAIL_HOST_USER

        members_email_body = render_to_string('emails/transfer.html', {
        'owner': member,
        'domain': current_site,
        'club':self.club
        })

        owner_email_body = render_to_string('emails/new_owner.html', {
        'owner': member,
        'domain': current_site,
        'club':self.club
        })

        email_to_members = self.club.members.exclude(id=member.id).values_list('email', flat=True)
        email_to_owner = [member.email]

        send_mail(subject, members_email_body, email_from, email_to_members)
        send_mail(subject, owner_email_body, email_from, email_to_owner)

        messages.add_message(self.request, messages.SUCCESS, "Ownership transferred!")
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        return reverse('club_page', kwargs={"club_id": self.club.id})


class EditClubInformationView(LoginRequiredMixin, UpdateView):
    """View that handles club information change requests."""
    model = Club
    fields = ['name', 'theme', 'meeting_type', 'club_type','city','country']
    template_name = "edit_club_info.html"
    pk_url_kwarg = "club_id"

    def get_context_data(self, **kwargs):
        """Set self.object to store club_id."""
        context = super().get_context_data(**kwargs)
        context['club_id'] = self.object.id
        return context

    def get_success_url(self):
        """Return URL to redirect the user to after valid form handling."""
        messages.add_message(self.request, messages.SUCCESS, "Successfully updated club information!")
        return reverse('club_page', args=[self.object.id])

"""Enables an owner to delete their club."""
@login_required
def delete_club(request, club_id):
    club = get_object_or_404(Club.objects, id=club_id)
    if(not request.user == club.owner):
        messages.add_message(request, messages.ERROR,
                             "Must be owner to delete club!")
        return redirect('club_page', club_id)

    club.delete()
    messages.add_message(request, messages.SUCCESS, "Deletion successful!")
    return redirect('home')