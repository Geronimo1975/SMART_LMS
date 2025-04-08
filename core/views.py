from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from courses.models import Course

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add some featured courses to the home page
        context['featured_courses'] = Course.objects.filter(is_active=True)[:3]
        return context

@login_required
def dashboard_view(request):
    # Get courses for the dashboard
    teaching_courses = Course.objects.filter(instructor=request.user, is_active=True)
    enrolled_courses = Course.objects.filter(students=request.user, is_active=True)
    
    return render(request, 'core/dashboard.html', {
        'user': request.user,
        'teaching_courses': teaching_courses,
        'enrolled_courses': enrolled_courses,
    })