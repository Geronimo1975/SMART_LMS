from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('signup/', views.CustomSignupView.as_view(), name='account_signup'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms-conditions/', views.TermsConditionsView.as_view(), name='terms_conditions'),
]