from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

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