from bookclub.forms import MeetingForm
from bookclub.helpers import MeetingHelper
from bookclub.models import Book, Club
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from system import settings

class ScheduleMeetingView(LoginRequiredMixin, FormView):
    template_name = "schedule_meeting.html"
    form_class = MeetingForm

    def get_context_data(self, **kwargs):
        """Extract club_id from self and store it in the context."""
        context = super().get_context_data(**kwargs)
        context["club_id"] = self.club_id
        return context

    def get_form_kwargs(self):
        """Generates data that the form needs to initialise."""
        kwargs = super().get_form_kwargs()
        kwargs["club"] = get_object_or_404(Club.objects, id=self.club_id)
        return kwargs

    def get(self, *args, **kwargs):
        """Extracts club id and stores it in self for later use."""
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
            deadline = timedelta(7).total_seconds() #0.00069444
            Timer(deadline, MeetingHelper().assign_rand_book, [meeting, self.request]).start()

        notify.send(self.club, recipient=self.club.members.all(), verb=NotificationHelper().NotificationMessages.SCHEDULE, action_object=meeting, description='club-event-M' )
        messages.add_message(self.request, messages.SUCCESS, "Meeting has been scheduled!")
        return redirect('club_page', club_id=self.club_id)

class ChoiceBookListView(LoginRequiredMixin, TemplateView):
    template_name = "choice_book_list.html"
    model = Book

    def get_context_data(self, *args, **kwargs):
        """Generate context data for the template."""
        context = super().get_context_data(*args, **kwargs)
        meeting = get_object_or_404(Meeting.objects, id=kwargs["meeting_id"])
        if self.request.user == meeting.chooser and not meeting.book:
            read_books = meeting.club.books.all()
            my_books =  Book.objects.all().exclude(id__in = read_books)
            context["rec_books"] = my_books.order_by('-average_rating','-readers_count')[0:24]
            return context
        else:
            raise Http404

class SearchBookView(LoginRequiredMixin, ListView):
    template_name = "choice_book_list.html"
    model = Book
    paginate_by = settings.BOOKS_PER_PAGE

    def get(self, request, *args, **kwargs):
        """Retrieves the searched term from the query string and stores it in self for later use."""
        self.searched = self.request.GET.get('searched', '')
        self.meeting_id = kwargs["meeting_id"]
        return super().get(request, *args, **kwargs)


    def get_queryset(self):
        """Returns filtered book list based on the searched term."""
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

"""Allow user to choose a book for a meeting."""
@login_required
def choose_book(request, book_id, meeting_id):
    meeting = get_object_or_404(Meeting.objects, id=meeting_id)
    if request.user == meeting.chooser and not meeting.book:
        book = get_object_or_404(Book.objects, id=book_id)
        meeting.assign_book(book)

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