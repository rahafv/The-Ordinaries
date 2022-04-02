from datetime import timedelta
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from .forms import SignUpForm, LogInForm, CreateClubForm, PasswordForm, UserForm, RatingForm , EditRatingForm, MeetingForm, BooksSortForm, UsersSortForm, ClubsSortForm, TransferOwnershipForm, BookForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .helpers import get_list_of_objects, generate_token, MeetingHelper, SortHelper, NotificationHelper, getGenres, get_recommender_books, rec_helper
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat, Meeting, User, Club, Book , Rating
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, FormView
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, send_mass_mail
from system import settings
from threading import Timer
from django.core.paginator import Paginator
from notifications.signals import notify
from notifications.utils import slug2id
from notifications.models import Notification
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import  DetailView, SingleObjectMixin
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, FormView, ListView, UpdateView
from django.views.generic.edit import FormMixin, CreateView
from django.utils.decorators import method_decorator
import humanize
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views.generic import ListView


def handler404(request, exception):
    return render(exception, '404_page.html', status=404)


@login_required
def mark_as_read(request, slug=None):
    notification_id = slug2id(slug)
    notification = get_object_or_404(Notification, recipient=request.user, id=notification_id)
    notification.mark_as_read()
    return NotificationHelper().get_appropriate_redirect(notification)




