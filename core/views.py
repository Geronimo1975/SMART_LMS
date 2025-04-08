from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'core/home.html'

@login_required
def dashboard_view(request):
    return render(request, 'core/dashboard.html')