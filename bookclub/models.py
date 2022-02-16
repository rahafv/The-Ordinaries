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
        blank=True
    )

    region = models.CharField(
        max_length=50,
        blank=True
    )

    country = models.CharField(
        max_length=50,
        blank=True
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

    class MeetingType(models.TextChoices):
        INPERSON = "IP", "In-person"
        ONLINE = "OL", "Online"

    meeting_type = models.CharField(
        max_length=2,
        choices=MeetingType.choices,
        default=MeetingType.INPERSON,
        blank=False,
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
            MinValueValidator(1)
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

    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE,
        related_name='meetings'
    )

    time = models.DateTimeField(
        auto_now_add=False,
        blank=False,
        null =False
    )

    link = models.URLField(
        max_length=1000,
        blank=False
    )

    notes = models.CharField(
        max_length=500,
        blank=True
    )
    

 

    

 

