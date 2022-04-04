from bookclub.forms import MeetingForm
from bookclub.helpers import MeetingHelper, NotificationHelper, get_recommender_books, rec_helper
from bookclub.models import Book, Club, Meeting, User
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic import FormView, ListView
from system import settings
from notifications.signals import notify
from threading import Timer

class ScheduleMeetingView(LoginRequiredMixin, FormView):
    """Enable club owner to schedule a meeting."""
    template_name = "meeting_templates/schedule_meeting.html"
    form_class = MeetingForm

    def get_context_data(self, **kwargs):
        """Extract club_id from self and store it in the context."""
        context = super().get_context_data(**kwargs)
        context["club_id"] = self.club_id
        return context

    def get_form_kwargs(self):
        """Generate data that the form needs to initialise."""
        kwargs = super().get_form_kwargs()
        kwargs["club"] = get_object_or_404(Club.objects, id=self.club_id)
        return kwargs

    def get(self, *args, **kwargs):
        """Extract club id and store it in self for later use."""
        self.club_id = kwargs["club_id"]
        self.club = get_object_or_404(Club.objects, id=self.club_id)
        if self.request.user != self.club.owner:
            raise Http404

        #check that the club has members
        if self.club.members.count() <= 1:
            messages.add_message(self.request, messages.ERROR, "There are no members!")
            return redirect('club_page', club_id=self.club.id)

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Check that user is owner upon form submission."""
        self.club_id = kwargs["club_id"]
        self.club = get_object_or_404(Club.objects, id=self.club_id)

        if self.request.user != self.club.owner:
            raise Http404

        return super().post(*args, **kwargs)

    def form_valid(self, form):
        """Process valid form."""
        meeting = form.save()
        #send email invites
        MeetingHelper().send_email(request=self.request,
            meeting=meeting,
            subject='A New Meeting Has Been Scheduled',
            letter='emails/meeting_invite.html',
            all_mem=True
        )

        if meeting.chooser:
            #send email to member who has to choose a book
            MeetingHelper().send_email(request=self.request,
                meeting=meeting,
                subject='It Is Your Turn!',
                letter='emails/chooser_reminder.html',
                all_mem=False
            )

            rec_book = get_recommender_books(self.request, True, 1, club_id=meeting.club.id)[0]
                        
            deadline = timedelta(7).total_seconds()  # 0.00069444
            Timer(deadline, MeetingHelper().assign_rand_book, [meeting, rec_book, self.request]).start()

        notify.send(self.club, recipient=self.club.members.all(), verb=NotificationHelper().NotificationMessages.SCHEDULE, action_object=meeting, description='club-event-M' )
        messages.add_message(self.request, messages.SUCCESS, "Meeting has been scheduled!")
        return redirect('club_page', club_id=self.club_id)

class ChoiceBookListView(LoginRequiredMixin, TemplateView):
    """Enable chosen user to choose a book for a club meeting."""
    template_name = "meeting_templates/choice_book_list.html"
    model = Book

    def get_context_data(self, *args, **kwargs):
        """Generate context data for the template."""
        context = super().get_context_data(*args, **kwargs)
        meeting = get_object_or_404(Meeting.objects, id=kwargs["meeting_id"])
        if self.request.user == meeting.chooser and not meeting.book:
            context["rec_books"] = get_recommender_books(self.request, True, 24, club_id=meeting.club.id)
            return context
        else:
            raise Http404

class SearchBookView(LoginRequiredMixin, ListView):
    """Enable user to search for specific books."""
    template_name = "meeting_templates/choice_book_list.html"
    model = Book
    paginate_by = settings.BOOKS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieve the searched term from the query string and store it in self for later use."""
        self.searched = self.request.GET.get('searched', '')
        self.meeting_id = kwargs["meeting_id"]
        return super().get(request, *args, **kwargs)


    def get_queryset(self):
        """Return filtered book list based on the searched term."""
        books = Book.objects.filter(title__contains=self.searched)
        return books

    def get_context_data(self, **kwargs):
        """Generate context data for the template."""
        context = super().get_context_data(**kwargs)
        meeting = get_object_or_404(Meeting.objects, id=self.meeting_id)
        if self.request.user == meeting.chooser and not meeting.book:
            context["searched"] = self.searched
            context["books"] = context["page_obj"]
            context["meeting_id"] = self.meeting_id
            return context
        else:
            raise Http404

class MeetingsListView(LoginRequiredMixin, ListView):
    """Display club's upcoming meetings list."""
    model = Meeting
    paginate_by = settings.MEMBERS_PER_PAGE

    def get(self, *args, **kwargs):
        """Store user and club in self."""
        self.user = get_object_or_404(User, id=self.request.user.id)
        self.club = get_object_or_404(Club, id=kwargs['club_id'])
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Return club's meetings."""
        if self.request.GET.get('filter') == 'Previous meetings': 
            self.is_previous = True
            return self.club.get_previous_meetings()

        if not self.request.GET.get('filter') or self.request.GET.get('filter') == 'Upcoming meetings':
            self.is_previous = False
            return self.club.get_upcoming_meetings()

        raise Http404

    def get_template_names(self):
        """Return a different template name if the user does not have access rights."""
        if self.club.is_member(self.user):
            return ['meeting_templates/meetings_list.html']
        else:
            messages.add_message(self.request, messages.ERROR, "You cannot access the meetings of the club" )
            return ['club_templates/club_page.html']
    
    def get_context_data(self, **kwargs):
        """Retrieve context data to be shown on the template."""
        context = super().get_context_data(**kwargs)
        context['meetings_list'] = context['page_obj']
        context['user'] = self.user
        context['club'] = self.club
        context['is_owner'] = self.request.user == self.club.owner
        context['is_previous'] = self.is_previous

        return context

"""Allow user to choose a book for a meeting."""
@login_required
def choose_book(request, book_id, meeting_id):
    meeting = get_object_or_404(Meeting.objects, id=meeting_id)
    if request.user == meeting.chooser and not meeting.book:
        book = get_object_or_404(Book.objects, id=book_id)
        meeting.assign_book(book)
        rec_helper.increment_counter()

        #send email to member who has to choose a book
        MeetingHelper().send_email(request=request,
            meeting=meeting,
            subject='A book has be chosen',
            letter='emails/book_confirmation.html',
            all_mem=True
        )

        messages.add_message(request, messages.SUCCESS,
                             "Book has been chosen!")
        notify.send(meeting, recipient=meeting.club.members.all(), verb=NotificationHelper().NotificationMessages.CHOICE, action_object=book, description='club-event-B' )

        return redirect('club_page', club_id=meeting.club.id)
    else:
        raise Http404

"""Enable club owner to cancel an upcoming meeting."""
@login_required
def cancel_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting.objects, id=meeting_id)
    club = get_object_or_404(Club.objects, id=meeting.club.id)
    user = request.user

    if (user == club.owner ):
        meeting.delete()
        messages.add_message(request, messages.SUCCESS, "You cancelled the meeting successfully!")

        """send email invites"""
        MeetingHelper().send_email(request=request,
                                    meeting=meeting,
                                    subject='A meeting has been cancelled ',
                                    letter='emails/meeting_cancelation_email.html',
                                    all_mem=True)

        return redirect('meetings_list', club.id)
    else:
        messages.add_message(request, messages.ERROR, "Must be owner to cancel a meeting!")
        return redirect('meetings_list', club.id)