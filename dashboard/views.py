from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from courses.models import Course, Assignment, Submission, Enrollment
from accounts.models import User
from .models import Notification
from django.utils import timezone
from datetime import timedelta

@login_required
def dashboard(request):
    user = request.user
    
    # Different dashboard for teachers and students
    if user.role == User.TEACHER:
        # Get courses taught by this teacher
        courses = Course.objects.filter(teacher=user)
        
        # Get recent submissions that need grading
        recent_submissions = Submission.objects.filter(
            assignment__course__teacher=user,
            is_graded=False
        ).order_by('-submitted_at')[:10]
        
        # Get upcoming assignments
        now = timezone.now()
        upcoming_assignments = Assignment.objects.filter(
            course__teacher=user,
            due_date__gt=now
        ).order_by('due_date')[:5]
        
        # Student count per course
        course_stats = []
        for course in courses:
            student_count = Enrollment.objects.filter(
                course=course, 
                is_active=True
            ).count()
            
            assignment_count = Assignment.objects.filter(
                course=course
            ).count()
            
            submission_count = Submission.objects.filter(
                assignment__course=course
            ).count()
            
            course_stats.append({
                'course': course,
                'student_count': student_count,
                'assignment_count': assignment_count,
                'submission_count': submission_count
            })
        
        # Recent notifications
        notifications = Notification.objects.filter(
            user=user,
            is_read=False
        )[:5]
        
        return render(request, 'dashboard/teacher_dashboard.html', {
            'courses': courses,
            'recent_submissions': recent_submissions,
            'upcoming_assignments': upcoming_assignments,
            'course_stats': course_stats,
            'notifications': notifications,
        })
    
    else:  # Student dashboard
        # Get courses the student is enrolled in
        enrollments = Enrollment.objects.filter(student=user, is_active=True)
        courses = Course.objects.filter(enrollments__in=enrollments)
        
        # Get upcoming assignments for enrolled courses
        now = timezone.now()
        upcoming_assignments = Assignment.objects.filter(
            course__in=courses,
            due_date__gt=now
        ).order_by('due_date')[:5]
        
        # Get recent submissions
        recent_submissions = Submission.objects.filter(
            student=user
        ).order_by('-submitted_at')[:5]
        
        # Get recent grades
        recent_grades = Submission.objects.filter(
            student=user,
            is_graded=True
        ).order_by('-grade__graded_at')[:5]
        
        # Get past due assignments that haven't been submitted
        past_due_assignments = Assignment.objects.filter(
            course__in=courses,
            due_date__lt=now
        ).exclude(
            submissions__student=user
        ).order_by('-due_date')[:5]
        
        # Recent notifications
        notifications = Notification.objects.filter(
            user=user,
            is_read=False
        )[:5]
        
        return render(request, 'dashboard/student_dashboard.html', {
            'courses': courses,
            'upcoming_assignments': upcoming_assignments,
            'recent_submissions': recent_submissions,
            'recent_grades': recent_grades,
            'past_due_assignments': past_due_assignments,
            'notifications': notifications,
        })

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'dashboard/notifications.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required
def mark_all_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications')
