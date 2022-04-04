from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, render
from bookclub.forms import BooksSortForm, ClubsSortForm, UsersSortForm
from bookclub.helpers import NotificationHelper, SortHelper, get_list_of_objects, get_recommender_books
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from bookclub.models import Book
from notifications.utils import slug2id
from django.core.paginator import Paginator
from system import settings
from notifications.models import Notification

class HomeView(TemplateView):
    """Display home view."""
    template_name = 'static_templates/home.html'

    def get_context_data(self, *args, **kwargs):
        """Genarate context data to be shown in the template."""
        context = super().get_context_data(*args, **kwargs)
        current_user = self.request.user
        
        if current_user.is_authenticated:
            notifications = current_user.notifications.unread()
            user_events = notifications.filter(description__contains ='user-event')[:25]
            club_events = notifications.filter(description__contains='club-event')[:10]
            top_rated_books = get_recommender_books(self.request, True, 3, user_id=current_user.id)
        else:
            notifications = None
            user_events = []
            club_events = []
            books = Book.objects.all()
            top_rated_books = books.order_by('-average_rating','-readers_count')[:3]

        context['club_events'] = list(club_events)
        context['club_events_length'] = len(club_events)
        context['user_events'] = list(user_events)
        context['books'] = top_rated_books
        return context

class ShowSortedView(LoginRequiredMixin, ListView):
    """Display sorted results of search."""
    template_name = 'static_templates/search_page.html'
    paginate_by = settings.MEMBERS_PER_PAGE

    def post(self, *args, **kwargs):
        """Handle post request."""
        return render(self.request, 'static_templates/search_page.html', {})

    def get(self, *args, **kwargs):
        """Handle get request."""
        self.searched = kwargs['searched']
        self.label = kwargs['label']
        search_page_results = get_list_of_objects(
            searched=kwargs['searched'], label=kwargs['label'])
        self.category = search_page_results["category"]
        self.filtered_list = search_page_results["filtered_list"]

        self.sortForm = ""
        if(self.category == "Clubs"):
            self.sortForm = ClubsSortForm(self.request.GET or None)
        elif(self.category == "Books"):
            self.sortForm = BooksSortForm(self.request.GET or None)
        else:
            self.sortForm = UsersSortForm(self.request.GET or None)

        sort = ""
        if (self.sortForm.is_valid()):
            sort = self.sortForm.cleaned_data.get('sort')
            sort_helper = SortHelper(sort, self.filtered_list)

            if(self.category == "Clubs"):
                self.filtered_list = sort_helper.sort_clubs()
            elif(self.category == "Books"):
                self.filtered_list = sort_helper.sort_books()
            else:
                self.filtered_list = sort_helper.sort_users()

        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Return filtered list based on search."""
        return self.filtered_list

    def get_context_data(self, **kwargs):
        """Retrieve context data to be shown on the template."""
        context = super().get_context_data(**kwargs)
        context['searched'] = self.searched
        context['label'] = self.label
        context['category'] = self.category
        context['form'] = self.sortForm
        context['filtered_list'] = context['page_obj']
        return context

class SearchPageView(LoginRequiredMixin, TemplateView):
    """Enable user to search for books, clubs, and users."""
    template_name = 'static_templates/search_page.html'
    paginate_by = settings.MEMBERS_PER_PAGE

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        searched = self.request.GET.get('searched')
        category = self.request.GET.get('category')
        label = category

        # method in helpers to return a dictionary with a list of users, clubs or books searched
        search_page_results = get_list_of_objects(
            searched=searched, label=label)
        category = search_page_results["category"]
        filtered_list = search_page_results["filtered_list"]

        sortForm = ""
        if(category == "Clubs"):
            sortForm = ClubsSortForm(self.request.GET or None)
        elif(category == "Books"):
            sortForm = BooksSortForm(self.request.GET or None)
        else:
            sortForm = UsersSortForm(self.request.GET or None)

        if (sortForm.is_valid()):
            sort = sortForm.cleaned_data.get('sort')
            sort_helper = SortHelper(sort, filtered_list)

            if(category == "Clubs"):
                filtered_list = sort_helper.sort_clubs()
            elif(category == "Books"):
                filtered_list = sort_helper.sort_books()
            else:
                filtered_list = sort_helper.sort_users()

        context['searched'] = searched
        context['category'] = category
        context['label'] = label
        pg = Paginator(filtered_list, settings.MEMBERS_PER_PAGE)
        page_number = self.request.GET.get('page')
        filtered_list = pg.get_page(page_number)
        context['filtered_list'] = filtered_list
        context['form'] = sortForm
        return context

"""Handle 404"""
def handler404(request, exception):
    return render(exception, 'static_templates/404_page.html', status=404)

"""Mark notification as read."""
@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)
    notification = get_object_or_404(Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return NotificationHelper().get_appropriate_redirect(notification)
