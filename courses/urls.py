from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('<slug:course_slug>/module/<int:module_id>/', views.module_detail, name='module_detail'),
    path('<slug:course_slug>/assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('<slug:course_slug>/submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
]