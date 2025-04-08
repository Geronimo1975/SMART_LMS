from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Profile
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already in use.')
        return email

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username or Email')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Check if the username is actually an email
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
        }

class TeacherProfileForm(ProfileForm):
    title = forms.CharField(max_length=100, required=False, help_text="Your academic or professional title")
    department = forms.CharField(max_length=100, required=False)
    office_hours = forms.CharField(max_length=255, required=False, help_text="e.g., Mon-Wed 2-4pm or By appointment")
    
    class Meta(ProfileForm.Meta):
        fields = ProfileForm.Meta.fields + ['title', 'department', 'office_hours']
