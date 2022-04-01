from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from libgravatar import Gravatar
from isbn_field import ISBNField
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
import pytz


class User(AbstractUser):
    """User model used for authentication."""

    email_verified = models.BooleanField(default=False)

    # training_counter = models.PositiveSmallIntegerField(
    #     null=False,
    #     blank=False
    # )

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

    all_books = models.ManyToManyField(
        "Book",
        related_name='+',
        blank = True
    )

    
    class Meta:
        ordering = ['first_name', 'last_name']

    def full_name(self):
        """Return full name."""
        return f'{self.first_name} {self.last_name}'

    def get_notifications(self):
        return self.notifications.unread().filter(description__contains ='notification')

    def location(self):
        checked = [self.city, self.country, self.region]
        location = []
        for state in checked:
            if state is not None:
                location.append(state)

        return ", ".join(location)

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

    def all_books_count(self):
        return self.all_books.all().count()

    def add_book_to_all_books(self , book):
        if book not in self.all_books.all():
            self.all_books.add(book)

    # def increment_counter(self):
    #     self.training_counter += 1
    #     self.save()

    # def reset_counter(self):
    #     self.training_counter = 0
    #     self.save()  


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

    created_at = models.DateTimeField(
        auto_now_add=True,
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

    def get_upcoming_meetings(self):
        upcoming_meetings = []
        for meeting in self.meetings.all():
            if meeting.time >= pytz.utc.localize(datetime.datetime.now()):
                upcoming_meetings.append(meeting)
        return upcoming_meetings

    def get_previous_meetings(self):
        previous_meetings = []
        for meeting in self.meetings.all():
            if meeting.time < pytz.utc.localize(datetime.datetime.now()):
                previous_meetings.append(meeting)
        return previous_meetings

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

    genre = models.CharField(
        max_length=100,
        unique=False,
        blank=True
    )

    description = models.CharField(
        max_length=500,
        unique=False,
        blank=True
    )

    image_url = models.URLField(
        blank=True,
        default='https://i.imgur.com/f6LoJwT.jpg'
    )

    pages_num = models.PositiveIntegerField(
        unique=False,
        blank=True,
        null=True
    )

    readers = models.ManyToManyField(
        User,
        related_name='books'
    )

    clubs = models.ManyToManyField(
        Club,
        related_name='books'
    )

    readers_count = models.PositiveIntegerField(
        default=0
    )

    average_rating = models.FloatField(
        default=0
    )

    class Meta:
        ordering = ['title']

    def is_reader(self, reader):
        return self.readers.all().filter(id=reader.id).exists()

    def add_reader(self, reader):
        if not self.is_reader(reader):
            self.readers.add(reader)
            self.readers_count = self.readers.count()
            self.save()

    def remove_reader(self, reader):
        if self.is_reader(reader):
            self.readers.remove(reader)
            self.readers_count = self.readers.count()
            self.save()

    def add_club(self, club):
        if not self.clubs.all().filter(id=club.id).exists():
            self.clubs.add(club)
            for member in club.members.all():
                self.add_reader(member)
                member.add_book_to_all_books(Book.objects.get(id=self.id))

            self.save()

    def clubs_count(self):
        return self.clubs.all().count()
     

    def calculate_average_rating(self):
        if self.ratings.all().count() != 0:
            sum = 0
            for rating in self.ratings.all():
                sum+= rating.rating
            self.average_rating = round(sum/self.ratings.all().count(), 2)
            self.save()


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


    def save(self, *args, **kwargs):
        super(Rating, self).save(*args, **kwargs)
        self.book.calculate_average_rating()


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

    class Meta:
        ordering = ['time']


    def assign_chooser(self):
        members = self.club.members
        meeting_ind = list(self.club.meetings.values_list('id', flat=True)).index(self.id)
        id = meeting_ind%members.count()
        mem = members.all()[id]
        self.chooser = mem
        Meeting.objects.filter(id = self.id).update(chooser=mem)

    def assign_book(self, book_in):
        book_in.add_club(self.club)
        self.book = book_in
        Meeting.objects.filter(id = self.id).update(book=book_in)


class Chat(models.Model):
    
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='chats'
    )

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
    )

    message = models.CharField(
        max_length=500,
        blank=False,
        null=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null =False
    )

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        super().clean()

        """ checks that the user is a member of the club """
        if not self.user in self.club.members.all():
            raise ValidationError('User must be a member of the club')
