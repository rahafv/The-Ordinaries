from datetime import date, datetime
from email.policy import default
from pickle import FALSE
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User, Club

class SignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'city', 'region', 'country', 'bio']
        widgets = { 'bio': forms.Textarea() }


    DOB = forms.DateField(initial= None, 
        label = 'Date of Birth',
        widget= forms.DateInput(),
        required= False, 
    )

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()

        self.DOB = self.cleaned_data.get('DOB')
        
        if not self.check_age(self.DOB):
            self.add_error('DOB', 'Please enter a valid date')

        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def check_age(self, dob):
        """Validate the age and check if it is an acceptable age."""
        try:
            return self.calculate_age(dob) < 100 and self.calculate_age(dob) > 10
        except:
            return True

    def calculate_age(self, dob):
        """Calculate the age from the given date input."""
        try:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age 
        except:
            age = None

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            age = self.calculate_age(self.DOB),
            email=self.cleaned_data.get('email'),
            city=self.cleaned_data.get('city'),
            region=self.cleaned_data.get('region'),
            country=self.cleaned_data.get('country'),
            bio=self.cleaned_data.get('bio'),
            password=self.cleaned_data.get('new_password'),
        )
        return user

class LogInForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

class CreateClubForm(forms.ModelForm):
    """Form to create or update club information."""
    
    class Meta:
        """Form options."""

        model = Club
        fields = ['name', 'theme', 'meeting_type', 'city', 'country']
        widgets = {"meeting_type": forms.Select()}