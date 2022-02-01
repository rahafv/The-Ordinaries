from unittest.util import _MAX_LENGTH
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from isbn_field import ISBNField
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from tempfile import NamedTemporaryFile

class User(AbstractUser):
    """User model used for authentication."""

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

    clubs = models.ManyToManyField(
        'Club',
        blank = True  
    )
    
    books = models.ManyToManyField(
        'Book', 
        related_name='books'
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
    
    members = models.ManyToManyField(
        'User', 
        related_name='members'
    )

    books = models.ManyToManyField(
        'Book', 
        related_name='clubBooks'
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

    def location(self):
        """Return full location."""
        return f'{self.city}, {self.country}'

    def add_member(self, member):
        if not self.members.all().filter(id=member.id).exists():
            self.members.add(member)

    def member_count(self):
        return self.members.all().count()   

class Book(models.Model):
    """Book model."""

    ISBN = ISBNField(
        unique=True
    )

    title = models.CharField(
        max_length=100,
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

    image_url = models.URLField( blank=True)

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
        related_name='readers'
    )

    def add_reader(self, reader):
        if not self.readers.all().filter(id=reader.id).exists():
            self.readers.add(reader)
    
    def readers_count(self):
        return self.readers.all().count()  

class Rating(models.Model):
    """rating model."""

    user =  models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE
    )

    review = models.CharField(max_length=250)

    rating = models.SmallIntegerField(
        default=0 , 
        blank = False , 
        validators=[
            MaxValueValidator(5) , 
            MinValueValidator(1)
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

 