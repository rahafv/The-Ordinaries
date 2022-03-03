from email import message
from email.policy import default
from pickle import FALSE
from pyclbr import Class
from queue import Empty
from unittest.util import _MAX_LENGTH
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from libgravatar import Gravatar
from isbn_field import ISBNField
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from tempfile import NamedTemporaryFile

class User(AbstractUser):
    """User model used for authentication."""

    email_verified = models.BooleanField(default=False)

    username = models.CharField(
        max_length=30,
        unique=True,
        blank=False
    )

    first_name = models.CharField(
        max_length=50,
        blank=False
    )

    last_name = models.CharField(
        max_length=50,
        blank=False
    )

    DOB = models.DateField(
        auto_now_add=False,
        blank=True,
        null =True,
        validators=[MaxValueValidator(limit_value=datetime.date.today)]
    )

    age = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    email = models.EmailField(
        unique=True,
        blank=False
    )

    city = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    region = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    country = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    bio = models.CharField(
        max_length=300,
        blank=True
    )

    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='followees'
    )

    class Meta:
        ordering = ['first_name', 'last_name']

    def full_name(self):
        """Return full name."""
        return f'{self.first_name} {self.last_name}'

    def location(self):
        """Return full location."""
        return f'{self.city}, {self.region},  {self.country}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def set_age(self,new_age):
        self.age = new_age
        return self.save()

    def toggle_follow(self, followee):
        """Toggles whether self follows the given followee."""
        #cant follow and unfollow self
        if followee==self:
            return
        #if following, unfollow
        if self.is_following(followee):
            self._unfollow(followee)
        else:
            self._follow(followee)

    def _follow(self, user):
        user.followers.add(self)

    def _unfollow(self, user):
        user.followers.remove(self)

    def is_following(self, user):
        """Returns whether self follows the given user."""

        return user in self.followees.all()

    def follower_count(self):
        """Returns the number of followers of self."""

        return self.followers.count()

    def followee_count(self):
        """Returns the number of followees of self."""

        return self.followees.count()

class Club(models.Model):
    """Club model."""

    name = models.CharField(
        max_length=50,
        blank=False,
        null=False
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    class MeetingType(models.TextChoices):
        INPERSON = "In-person"
        ONLINE = "Online"

    meeting_type = models.CharField(
        max_length=9,
        choices=MeetingType.choices,
        default=MeetingType.INPERSON,
        blank=False,
    )

    class ClubType(models.TextChoices):
        PRIVATE =  "Private"
        PUBLIC =  "Public"

    club_type = models.CharField(
        max_length = 7,
        choices = ClubType.choices,
        default=ClubType.PUBLIC,
        blank = False
    )

    members = models.ManyToManyField(
        User,
        related_name='clubs'
    )

    applicants = models.ManyToManyField(
        User,
        related_name='clubs_applied_to',
    )

    theme = models.CharField(
        max_length=100,
        blank=True
    )

    city = models.CharField(
        max_length=50,
        blank=True
    )

    country = models.CharField(
        max_length=50,
        blank=True
    )

    class Meta:
        ordering = ['name']

    def location(self):
        """Return full location."""
        return f'{self.city}, {self.country}'

    def add_member(self, member):
        if not self.members.all().filter(id=member.id).exists():
            self.members.add(member)

    def member_count(self):
        return self.members.all().count()

    def is_member(self, user):
        """ checks if the user is a member"""
        return self.members.all().filter(id=user.id).exists()

    def add_applicant(self, applicant):
        self.applicants.add(applicant)

    def applicants_count(self):
        return self.applicants.all().count()

    def is_applicant(self, user):
        """ checks if the user is a member"""
        return self.applicants.all().filter(id=user.id).exists()

    def get_club_type_display(self):
        return self.club_type


    def make_owner(self, new_owner):
        self.owner = new_owner
        self.save()

class Book(models.Model):
    """Book model."""

    ISBN = ISBNField(
        unique=True
    )

    title = models.CharField(
        max_length=200,
        unique=False,
        blank=False
    )

    author = models.CharField(
        max_length=100,
        unique=False,
        blank=False
    )

    publisher = models.CharField(
        max_length=100,
        unique=False,
        blank=True
    )

    image_url = models.URLField(
        blank=True
    )

    year = models.PositiveIntegerField(
        default=datetime.datetime.now().year,
        blank=True,
        validators=[
            MaxValueValidator(datetime.datetime.now().year),
            MinValueValidator(0)
        ]
    )

    readers = models.ManyToManyField(
        User,
        related_name='books'
    )

    clubs = models.ManyToManyField(
        Club,
        related_name='books'
    )

    class Meta:
        ordering = ['title']

    def is_reader(self, reader):
        return self.readers.all().filter(id=reader.id).exists()

    def add_reader(self, reader):
        if not self.is_reader(reader):
            self.readers.add(reader)

    def remove_reader(self, reader):
        if self.is_reader(reader):
            self.readers.remove(reader)

    def readers_count(self):
        return self.readers.all().count()

    def add_club(self, club):
        if not self.clubs.all().filter(id=club.id).exists():
            self.clubs.add(club)

    def clubs_count(self):
        return self.clubs.all().count()

    def average_rating(self):
        sum = 0.0
        if self.ratings.all().count() != 0:
            for rating in self.ratings.all():
                sum+= rating.rating
            return (sum/self.ratings.all().count())
        else:
            return 0.0

class Rating(models.Model):
    """rating model."""

    user =  models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    review = models.CharField(
        max_length=250 ,
        blank = True
    )

    rating = models.FloatField(
        blank=True,
        default=0,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(0)
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'book']

class Meeting(models.Model):
    """ The meeting model."""

    title = models.CharField(
        max_length=50,
        blank=False,
        null=False
    )

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='meetings'
    )

    chooser = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='rotations',
        blank=True, 
        null=True
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='meetings',
        blank=True, 
        null=True
    )

    time = models.DateTimeField(
        auto_now_add=False,
        blank=False,
        null =False
    )

    notes = models.CharField(
        max_length=500,
        blank=True
    )

    link = models.URLField(
        max_length=1000,
        blank=True
    )

    def assign_chooser(self):
        members = self.club.members
        meeting_ind = list(self.club.meetings.values_list('id', flat=True)).index(self.id)
        id = meeting_ind%members.count()
        mem = members.all()[id]
        self.chooser = mem
        Meeting.objects.filter(id = self.id).update(chooser=mem)

    def assign_book(self, book_in=None):
        if not book_in:
            read_books = self.club.books.all()
            book_in = Book.objects.all().exclude(id__in = read_books).order_by("?")[0]
        else:
            book_in.add_club(self.club)
        
        self.book = book_in
        Meeting.objects.filter(id = self.id).update(book=book_in)

        
ACTOR_CHOICES = (
    ('U', 'User'),
    ('C', 'Club'),
)
ACTION_CHOICES = (
    ('B', 'Book'),
    ('C', 'Club'),
    ('M', 'Meeting'),
    ('R', 'Rating'),
    ('U', 'Action_User')
)

class Event(models.Model):
    """Events by users or clubs."""

    """To allow to types of actors of the event"""
    type_of_actor = models.CharField(max_length=1, choices=ACTOR_CHOICES)

    """To identify the type of action the actor is responsible for"""
    type_of_action = models.CharField(max_length=1, choices=ACTION_CHOICES)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='events')
    club = models.ForeignKey(Club, blank=True, null=True, on_delete=models.CASCADE , related_name='events')
    meeting = models.ForeignKey(Meeting, blank=True, null=True, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, blank=True, null=True, on_delete=models.CASCADE)
    rating = models.ForeignKey(Rating, blank=True, null=True, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    action_user =  models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        """Model options."""

        ordering = ['-created_at']

    def clean(self):

        super().clean()

        """ checks that the type of actor and the object are correct """
        if self.type_of_actor == 'U' and not self.user:
            raise ValidationError('Actor must be User')
        if self.type_of_actor == 'C' and not self.club:
            raise ValidationError('Actor must be Club')


        """Restrictions on the actors and their allowed actions"""
        if self.type_of_actor == 'U' and self.type_of_action == 'M':
            raise ValidationError('User cannot generate a meeting')

        if self.type_of_actor == 'C' and self.type_of_action == 'R':
            raise ValidationError('Club cannot rate')
        if self.type_of_actor == 'C' and self.type_of_action == 'C':
            raise ValidationError('Club cannot create club')
        if self.type_of_actor == 'C' and self.type_of_action == 'U':
            raise ValidationError('Club cannot join and withdraw from clubs')

        """ checks that the type of actor and the object are correct """
        if self.type_of_action == 'B' and not self.book:
            raise ValidationError('Action must be Book')
        if self.type_of_action == 'C' and not self.club:
            raise ValidationError('Action must be Club')
        if self.type_of_action == 'M' and not self.meeting:
            raise ValidationError('Action must be meeting')
        if self.type_of_action == 'R' and not self.rating:
            raise ValidationError('Action must be rating')
        if self.type_of_action == 'U' and not self.action_user:
            raise ValidationError('Action must be user')

    def save(self, **kwargs):
        self.clean()
        return super(Event, self).save(**kwargs)

    class EventType(models.TextChoices):

        JOIN = " joined "
        WITHDRAW = " withdrew from "
        FOLLOW =  " followed "
        CREATE = " created "
        REVIEW = " reviewed "
        ADD = " added "
        SCHEDULE = " scheduled a meeting about "
        
    def get_actor(self):
        """Return the actor of a given event."""
        if self.type_of_actor == 'U':
            return self.user.username
        else:
            return self.club.name

    def get_action(self):
        """Return the actor of a given event."""
        if self.type_of_action == 'C':
            return self.club.name
        elif self.type_of_action == 'B':
            return self.book.title
        elif self.type_of_action == 'U':
            return self.action_user.username
        elif self.type_of_action == 'M':
            return self.meeting.title
        else:
            return self.rating.book.title
