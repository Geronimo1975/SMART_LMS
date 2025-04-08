from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['gdpr_consent', 'marketing_consent', 'terms_accepted']
        widgets = {
            'gdpr_consent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'marketing_consent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'terms_accepted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'gdpr_consent': 'I consent to my personal data being processed as described in the Privacy Policy',
            'marketing_consent': 'I would like to receive marketing information about products and services',
            'terms_accepted': 'I accept the Terms and Conditions',
        }

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)
    gdpr_consent = forms.BooleanField(
        required=True,
        label='I consent to my personal data being processed as described in the Privacy Policy',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    marketing_consent = forms.BooleanField(
        required=False,
        label='I would like to receive marketing information about products and services',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    terms_accepted = forms.BooleanField(
        required=True,
        label='I accept the Terms and Conditions',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # Get profile
        profile = user.profile
        profile.gdpr_consent = self.cleaned_data.get('gdpr_consent', False)
        profile.marketing_consent = self.cleaned_data.get('marketing_consent', False)
        profile.terms_accepted = self.cleaned_data.get('terms_accepted', False)
        profile.save()
        
        return user