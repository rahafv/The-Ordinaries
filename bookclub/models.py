from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
#from isbn_field import ISBNField
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

    
    books = models.ManyToManyField('Book', related_name='books')
  
    class Meta:
        ordering = ['first_name', 'last_name']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def location(self):
        return f'{self.city}, {self.region},  {self.country}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url
    



class Book(models.Model):
    """Book model."""

    ISBN = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')

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

    image_url = models.URLField()

    year = models.PositiveIntegerField(
        default=datetime.datetime.now().year,
        blank=True,
        validators=[
            MaxValueValidator(datetime.datetime.now().year),
            MinValueValidator(1)
        ]
    )

    readers = models.ManyToManyField(User, related_name='clubs')