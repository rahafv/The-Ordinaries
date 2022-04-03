from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
import humanize
from bookclub.models import Chat, Club, User
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required


class ChatRoomView(LoginRequiredMixin, TemplateView):
    """Display user chats."""
    template_name = "chat_room.html"
    pk_url_kwarg = "club_id"

    def get(self, *args, **kwargs):
        """Handle get request and perform checks on whether a user is a member
        of a club and if the club has more than one member before displaying chats. """
        user = self.request.user
        club = get_object_or_404(Club, id=kwargs['club_id']) if 'club_id' in kwargs else None

        if club:
            if not club.is_member(user):
                raise Http404

            if club.members.count() <= 1:
                messages.add_message(self.request, messages.INFO, "This club have one member only. More members should join to start a conversation")
                return redirect('club_page' , club_id = club.id)
                
        else:
            clubs = user.clubs.all()
            if clubs:
                club = None
                for c in clubs:
                    if c.members.count() > 1:
                        club = c
                        break
                if not club:
                    messages.add_message(self.request, messages.INFO, "All your clubs have one member. Join more clubs and be part of a community.")
                    return redirect('clubs_list')
            else:
                messages.add_message(self.request, messages.INFO, "You do not have any chats! Join clubs and be part of a community.")
                return redirect('clubs_list')
        return render(self.request, "chat_room.html", {"club":club})

"""Get club's chat messages."""
@login_required
def getMessages(request, club_id):
    if request.is_ajax():
        club = get_object_or_404(Club.objects, id=club_id)
        current_user = request.user

        chats = list(club.chats.all().values())[:200]
        modifiedItems = []
        for key in chats:
            user_id = key.get("user_id")
            user = get_object_or_404(User.objects, id=user_id)
            prettyDate = humanize.naturaltime(key.get("created_at").replace(tzinfo=None))
            modifiedItems.append({"name": user.full_name(), "time":prettyDate})

        return JsonResponse({"chats":chats, "modifiedItems":modifiedItems, "user_id":current_user.id})
    raise Http404
    
"""Send a message in the chat."""
@login_required
def send(request):
    if request.method == "POST":
        message = request.POST['message']

        if message.strip():
            username = request.POST['username']
            club_id = request.POST['club_id']

            club = get_object_or_404(Club.objects, id=club_id)
            user = get_object_or_404(User.objects, username=username)

            new_chat_msg = Chat.objects.create(club=club, user=user, message=message)
            new_chat_msg.save()

        return HttpResponse('Message sent successfully')
    raise Http404