from django.urls import path
from . import views

urlpatterns = [
    # Course views
    path('', views.course_list, name='course_list'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('create/', views.course_create, name='course_create'),
    path('<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),
    
    # Assignment views
    path('<int:course_id>/assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    
    # Submission views
    path('assignments/<int:assignment_id>/submit/', views.submission_create, name='submission_create'),
    path('submissions/<int:pk>/view/', views.submission_detail, name='submission_detail'),
    
    # Material views
    path('<int:course_id>/materials/create/', views.material_create, name='material_create'),
    path('materials/<int:pk>/', views.material_detail, name='material_detail'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    
    # Enrollment views
    path('<int:course_id>/enroll/', views.enroll_in_course, name='enroll_in_course'),
    path('<int:course_id>/unenroll/', views.unenroll_from_course, name='unenroll_from_course'),
    path('<int:course_id>/manage-students/', views.manage_students, name='manage_students'),
    
    # Grading views
    path('submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
]
