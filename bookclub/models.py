from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

class User(AbstractUser):
    """User model used for authentication."""

    username = models.CharField(
        max_length=30,
        unique=True
    )

    first_name = models.CharField(
        max_length=50,
        blank=False
    )

    last_name = models.CharField(
        max_length=50,
        blank=False
    )

    birthdate = models.DateField(
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

    state = models.CharField(
        max_length=50,
        blank=True
    )

    country = models.CharField(
        max_length=50,
        blank=True
    )

    bio = models.CharField(
        max_length=520,
        blank=True
    )
  
    class Meta:
        ordering = ['first_name', 'last_name']

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def age(self):
        import datetime
        return int( (datetime.date.today() - self.birthdate).days / 365.25 )

    def location(self):
        return f'{self.city}, {self.state},  {self.country}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)
