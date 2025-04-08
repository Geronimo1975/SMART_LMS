from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gdpr_consent', 'marketing_consent', 'terms_accepted', 'consent_date')
    list_filter = ('gdpr_consent', 'marketing_consent', 'terms_accepted')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'consent_date'