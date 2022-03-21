from datetime import date, datetime, timedelta
from django import forms
from django.core.validators import RegexValidator
import pytz
from .models import Chat, User, Club, Book, Rating, Meeting
from django.contrib.auth import authenticate

class SignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email','DOB', 'city', 'region', 'country', 'bio']
        widgets = { 'bio': forms.Textarea(), 'DOB': forms.DateInput(attrs={'type': 'date'}) }

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
            DOB=self.cleaned_data.get('DOB'),
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

    def get_user(self):
        """Returns authenticated user if possible."""
    
        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user

class CreateClubForm(forms.ModelForm):
    """Form to create or update club information."""

    class Meta:
        """Form options."""

        model = Club
        fields = ['name', 'theme', 'meeting_type', 'club_type', 'city', 'country']
        widgets = {"meeting_type": forms.Select(), "club_type":forms.Select()}
        labels = {'club_type': "Select Club Privacy Status"}

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number.'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        password = self.cleaned_data.get('password')
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')
        if password == new_password:
            self.add_error('new_password', 'Your new password cannot be the same as your current one')

class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""

        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None

        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        self.user.set_password(new_password)
        self.user.save()
        return self.user

class BookForm(forms.ModelForm):
    """Form enabling a user to create a book."""

    class Meta:
        """Form options."""
        model = Book
        fields = ['ISBN','title','author', 'genre', 'image_url', 'describtion']

    def clean(self):
        self.oldISBN = self.cleaned_data.get('ISBN')
        if self.oldISBN:
            self.ISBN = self.oldISBN.replace('-', '').replace(' ', '')
            if Book.objects.filter(ISBN=self.ISBN).exists():
                self.add_error('ISBN', 'ISNB already exists')

    def save(self):
        """Create a new book."""

        super().save(commit=False)

        book = Book.objects.create(
            ISBN=self.cleaned_data.get('ISBN'),
            title=self.cleaned_data.get('title'),
            author=self.cleaned_data.get('author'),
            genre=self.cleaned_data.get('genre'),
            image_url=self.cleaned_data.get('image_url'),
            describtion=self.cleaned_data.get('describtion'),
        )
        return book


class UserForm(forms.ModelForm):
    """Form to update user profile."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email','DOB', 'city', 'region', 'country', 'bio']
        widgets = { 'bio': forms.Textarea(), 'DOB': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        """ Grants access to the request object so that the date of birth can be changed"""

        self.log_in_user = kwargs.pop('user',None)
        super(UserForm, self).__init__(*args, **kwargs)


    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()

        self.DOB = self.cleaned_data.get('DOB')

        if not self.check_age(self.DOB):
            self.add_error('DOB', 'Please enter a valid date')

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
        """Save user."""
        super().save(commit=False)
        birthdate= self.cleaned_data.get('DOB')
        new_age = self.calculate_age(birthdate)
        self.log_in_user.set_age(new_age)
        return self.log_in_user


class EditRatingForm(forms.ModelForm):
    """Form to update club information."""

    class Meta:

        model = Rating
        fields = ['rating', 'review']


    def calculate_rating(self, rating):
        return rating*2

    def save(self , reviwer, reviewedBook):
        super().save(commit=False)
        rate = self.cleaned_data.get('rating')
        if not rate:
            rate = 0
        review_obj = Rating.objects.get(user=reviwer , book=reviewedBook)
        review_obj.rating=self.calculate_rating(rate)
        review_obj.review=self.cleaned_data.get('review')
        review_obj.save()    
         

class RatingForm(forms.ModelForm):
    """Form to post a review."""
    
    class Meta:

        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'review': forms.Textarea(attrs={'cols': 40, 'rows': 15}),
        }


    def save(self, reviwer, reviewedBook):
        """Create a new rating."""
        super().save(commit=False)
        rate = self.cleaned_data.get('rating')
        if not rate:
            rate = 0
        review = Rating.objects.create(
            rating = self.calculate_rating(rate),
            review = self.cleaned_data.get('review'),
            book = reviewedBook,
            user = reviwer,
        )
        return review

    def calculate_rating(self, rating): 
        return rating*2

class UsersSortForm(forms.Form):
    
    ASCENDING = 'name_asc'
    DESCENDING = 'name_desc'

    SORT_CHOICES = [
        (ASCENDING, "Name A-Z"),
        (DESCENDING, "Name Z-A")
    ]   
    
    sort = forms.ChoiceField(
        required = False,
        choices = SORT_CHOICES, 
        initial = ASCENDING, 
    )

    widgets = {'sort': forms.Select()}       
   
   
class ClubsSortForm(forms.Form):

    ASC_DATE = "date_asc"
    DESC_DATE = "date_desc"
    ASC_NAME = 'name_asc'
    DESC_NAME = 'name_desc'

    SORT_CHOICES = [
        (ASC_NAME, "Name A-Z"),
        (DESC_NAME, "Name Z-A"),
        (DESC_DATE, "Latest"),
        (ASC_DATE, "Oldest"),
    ]

    sort = forms.ChoiceField(
      required = False,
      choices=SORT_CHOICES,
      label='Sort by:',
      initial = ASC_NAME,
      widget=forms.Select(),
    )

   
class BooksSortForm(forms.Form):

    ASC_NAME = 'name_asc'
    DESC_NAME = 'name_desc'
    ASC_RATING = 'rating_asc'
    DESC_RATING = 'rating_desc'

    SORT_CHOICES = [
        (ASC_NAME, "Name A-Z"),
        (DESC_NAME, "Name Z-A"),
        (DESC_RATING, "High rating"),
        (ASC_RATING, "Low rating"),
       
    ]

    sort = forms.ChoiceField(
      required = False,
      choices=SORT_CHOICES,
      label='Sort by:',
      initial = ASC_NAME,
      widget=forms.Select(),
    )

 
class MeetingForm(forms.ModelForm):
    """Form to update club information."""

    class Meta:
        """Form options."""

        model = Meeting
        fields = ['title', 'time', 'notes', 'link']
        widgets = {
            'time': forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'cols': 40, 'rows': 15}),
        }
        exclude = ['club', 'book', 'member']

    cont = forms.BooleanField(
        label = "This meeting a continuation of a previous discussion",
        required = False,
        help_text = "checkbox",
        label_suffix=""
    )

    def __init__(self, club, *args, **kwargs):
        self.club = club
        super(MeetingForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        super().clean()
        if not self.cleaned_data.get('link'):
            if self.club.meeting_type == Club.MeetingType.ONLINE:
                self.add_error('link', "Provide a link to the meeting.")
            else:
                self.add_error('link', "Provide a link to the meeting location.")

        is_cont = self.cleaned_data.get('cont')
        time = self.cleaned_data.get('time')

        self.check_date(time, is_cont)
        self.check_meetings(time, is_cont)

        return self.cleaned_data

    def check_date(self, time, is_cont):
        """Validate the time and check if it is appropriate."""
        today = datetime.today()
        start_week = today + timedelta(13)
        try:
            if not is_cont and time < pytz.utc.localize(start_week):
                self.add_error('time', 'Date should be at least 2 weeks from today.')
            else:
                if time.day == today.day and time.month == today.month and time.year == today.year:
                    self.add_error('time', 'Date cannot be today.')
        except:
            pass

    def check_meetings(self, time, is_cont):
        """Check if there are meetings in the same period."""
        if time:
            meetings = Meeting.objects.filter(club_id=self.club.id)
            for met in meetings:
                if not is_cont:
                    if met.time+timedelta(30) > time:
                        self.add_error('time', 'Meetings should be at least a month apart.')
                        break
                else:
                    if met.time.day == time.day and met.time.month == time.month and met.time.year == time.year:
                        self.add_error('time', 'There is a meeting on that day.')
                        break
            if meetings.count() == 0 :
                if is_cont:
                    self.add_error('cont', "There are no previous meetings.")


    def save(self):
        """Create a new meeting."""
        super().save(commit=False)
        meeting = Meeting.objects.create(
            title = self.cleaned_data.get('title'),
            club = self.club,
            time = self.cleaned_data.get('time'),
            notes = self.cleaned_data.get('notes'),
            link = self.cleaned_data.get('link'),
        )
        if not self.cleaned_data.get('cont'):
            meeting.assign_chooser()
        return meeting

class TransferOwnershipForm(forms.Form):
    def __init__(self, *args, **kwargs):
        club_id = kwargs.pop("club_id")
        user_id = kwargs.pop("user_id")
        super().__init__(*args, **kwargs)
        self.fields["new_owner"] = forms.ModelChoiceField(queryset=Club.objects.get(id=club_id).members.all().exclude(id=user_id), label="Please select a new owner")
        self.fields["confirm"] = forms.BooleanField(label="Please confirm by checking this box", widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
