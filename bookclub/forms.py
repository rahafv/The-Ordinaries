from cProfile import label
from calendar import month
from datetime import date, datetime
from email import message
from email.policy import default
from pickle import FALSE
import this
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User

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

class UserForm(forms.ModelForm):
    """Form to update user profile."""
    
    class Meta:
        """Form options."""

        model = User
        fields = ['username', 'first_name', 'last_name','email', 'city', 'region','country','bio']
        widgets = { 'bio': forms.Textarea()} # 'age':forms.DateInput()}
        # labels = {'age':'Date of birth'}
        # initial = {'age': date.today()}

    date_of_birth = forms.DateField( 
    label = 'Date of Birth',
    widget= forms.DateInput(),
    required= True, 
    )

    def __init__(self, *args, **kwargs):
        """ Grants access to the request object so that the date of birth can be displayed"""

        self.request = kwargs.pop('request')
        super(UserForm, self).__init__(*args, **kwargs)
        log_in_user = self.request.user
        print(f'{log_in_user.age} {log_in_user.username}')
        today = date.today()
        year_of_birth = today.year - log_in_user.age
        # initial_date = datetime.date(day = today.day, month = today.month, year = year_of_birth)       
        # self.fields['date_of_birth'].initial = initial_date
        print(self.fields['date_of_birth'].initial)
            


    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()

        self.date_of_birth = self.cleaned_data.get('date_of_birth')
        
        if not self.check_age(self.date_of_birth):
            self.add_error('date_of_birth', 'Please enter a valid date in the format "dd/mm/yyyy"')


    def check_age(self, date_of_birth):
        """Validate the age and check if it is an acceptable age."""
        try:
            return self.calculate_age(date_of_birth) < 100 and self.calculate_age(date_of_birth) > 10
        except:
            return True
    
    def calculate_age(self, dob):
        """Calculate the age from the given date input."""
        today = date.today()
    
        # A bool that represents if today's day/month precedes the birth day/month
        one_or_zero = ((today.month, today.day) < (dob.month, dob.day))
        
        # Calculate the difference in years from the date object's components
        year_difference = today.year - dob.year
        age = year_difference - one_or_zero
        print(f'{age}')
        
        return age

    # def check_dob_is_valid(self, date_of_birth):
    #     if date_of_birth.day > 0 and date_of_birth.day < 32 and date_of_birth.month > 0 and date_of_birth.month <= 12:
    #         if date_of_birth.year == date.today().year:
    #             if date_of_birth.month <= date.today().month and date_of_birth.day <= date.today().day:
    #                 return True
    #             else: 
    #                 self.add_error('date_of_birth', 'Please enter a valid date in the format "dd/mm/yyyy"')
    #                 return False
    #         elif date_of_birth.year < date.today().year:
    #             return True

    #     else:
    #         self.add_error('date_of_birth', 'Please enter a valid date in the format "dd/mm/yyyy"')
    #         return False


    # def calculate_age(self, date_of_birth):
    #     """Calculate the age from the given date input."""
    #     # if self.check_dob_is_valid(date_of_birth):
    #     today = date.today()
    #     age = today.year - date_of_birth.year
    #     if ((today.month, today.day) < (date_of_birth.month, date_of_birth.day)):
    #         age += 1
    #     return age 
    #     # else:
    #     #     self.add_error('date_of_birth', 'Please enter a valid date in the format "dd/mm/yyyy"')


    def save(self):
        """Save user."""
        log_in_user = self.request.user
        birthdate= self.date_of_birth
        new_age = self.calculate_age(birthdate)  
        print(f'{new_age}')
        log_in_user.set_age(new_age)
        return log_in_user