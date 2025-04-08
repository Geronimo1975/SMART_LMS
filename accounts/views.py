from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from .models import UserProfile
from allauth.account.views import SignupView
from .forms import UserProfileForm, CustomSignupForm

class CustomSignupView(SignupView):
    form_class = CustomSignupForm
    template_name = 'accounts/signup.html'

@login_required
def profile_view(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'accounts/profile.html', context)

class PrivacyPolicyView(TemplateView):
    template_name = 'legal/privacy_policy.html'

class TermsConditionsView(TemplateView):
    template_name = 'legal/terms_conditions.html'