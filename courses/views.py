from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q
from .models import Course, Module, Content, Assignment, Submission
from .forms import AssignmentSubmissionForm


def course_list(request):
    """Display a list of all active courses"""
    if request.user.is_authenticated:
        # For authenticated users, show courses they're teaching or enrolled in
        teaching_courses = Course.objects.filter(instructor=request.user, is_active=True)
        enrolled_courses = Course.objects.filter(students=request.user, is_active=True)
        available_courses = Course.objects.filter(is_active=True).exclude(
            Q(instructor=request.user) | Q(students=request.user)
        )
        
        context = {
            'teaching_courses': teaching_courses,
            'enrolled_courses': enrolled_courses,
            'available_courses': available_courses,
        }
    else:
        # For anonymous users, just show active courses
        courses = Course.objects.filter(is_active=True)
        context = {'available_courses': courses}
    
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    """Display details of a specific course"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # Check if user is instructor or enrolled student
    is_instructor = request.user == course.instructor
    is_enrolled = request.user in course.students.all()
    can_access = is_instructor or is_enrolled
    
    # Get modules if user can access the course
    modules = None
    if can_access:
        modules = course.modules.all().prefetch_related('contents', 'assignments')
    
    # Check if course has an AI assistant
    has_assistant = False
    assistant_id = None
    if hasattr(course, 'ai_assistant'):
        has_assistant = True
        assistant_id = course.ai_assistant.id
    
    context = {
        'course': course,
        'modules': modules,
        'is_instructor': is_instructor,
        'is_enrolled': is_enrolled,
        'has_assistant': has_assistant,
        'assistant_id': assistant_id,
    }
    
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, slug):
    """Enroll a student in a course"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    if request.user == course.instructor:
        messages.error(request, "You cannot enroll in your own course!")
        return redirect('course_detail', slug=slug)
    
    if request.user in course.students.all():
        messages.info(request, "You are already enrolled in this course.")
    else:
        course.students.add(request.user)
        messages.success(request, f"You have successfully enrolled in {course.title}!")
    
    return redirect('course_detail', slug=slug)


@login_required
def module_detail(request, course_slug, module_id):
    """Display details of a specific module"""
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Check if user is instructor or enrolled student
    if not (request.user == course.instructor or request.user in course.students.all()):
        return HttpResponseForbidden("You do not have access to this module.")
    
    contents = module.contents.all().order_by('order')
    assignments = module.assignments.all()
    
    # For each assignment, check if the current user has submitted
    if request.user != course.instructor:
        for assignment in assignments:
            assignment.user_submission = assignment.submissions.filter(student=request.user).first()
    
    context = {
        'course': course,
        'module': module,
        'contents': contents,
        'assignments': assignments,
        'is_instructor': request.user == course.instructor,
    }
    
    return render(request, 'courses/module_detail.html', context)


@login_required
def assignment_detail(request, course_slug, assignment_id):
    """Display details of a specific assignment and handle submissions"""
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    assignment = get_object_or_404(Assignment, id=assignment_id, module__course=course)
    
    # Check if user is instructor or enrolled student
    if not (request.user == course.instructor or request.user in course.students.all()):
        return HttpResponseForbidden("You do not have access to this assignment.")
    
    # Handle assignment submission (students only)
    submission = None
    form = None
    
    if request.user != course.instructor:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        
        if request.method == 'POST' and (not submission or submission.status == 'returned'):
            form = AssignmentSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                if submission:
                    # Update existing submission
                    submission.file = form.cleaned_data.get('file')
                    submission.text = form.cleaned_data.get('text')
                    submission.submitted_at = timezone.now()
                    submission.status = 'submitted'
                    submission.save()
                    messages.success(request, "Your submission has been updated.")
                else:
                    # Create new submission
                    submission = form.save(commit=False)
                    submission.assignment = assignment
                    submission.student = request.user
                    submission.save()
                    messages.success(request, "Your assignment has been submitted successfully.")
                return redirect('assignment_detail', course_slug=course_slug, assignment_id=assignment_id)
        else:
            form = AssignmentSubmissionForm(instance=submission)
    else:
        # For instructors, get all submissions
        submissions = assignment.submissions.all().select_related('student')
        context = {
            'course': course,
            'assignment': assignment,
            'submissions': submissions,
            'is_instructor': True,
        }
        return render(request, 'courses/assignment_instructor_view.html', context)
    
    context = {
        'course': course,
        'assignment': assignment,
        'submission': submission,
        'form': form,
        'is_instructor': False,
    }
    
    return render(request, 'courses/assignment_detail.html', context)


@login_required
def grade_submission(request, course_slug, submission_id):
    """Allow instructors to grade student submissions"""
    course = get_object_or_404(Course, slug=course_slug, is_active=True)
    submission = get_object_or_404(Submission, id=submission_id, assignment__module__course=course)
    
    # Only the course instructor can grade submissions
    if request.user != course.instructor:
        return HttpResponseForbidden("You do not have permission to grade this submission.")
    
    if request.method == 'POST':
        score = request.POST.get('score')
        feedback = request.POST.get('feedback')
        status = request.POST.get('status', 'graded')
        
        if score and score.isdigit():
            submission.score = int(score)
            submission.feedback = feedback
            submission.status = status
            submission.save()
            messages.success(request, f"Submission by {submission.student.username} has been graded.")
        else:
            messages.error(request, "Please provide a valid score.")
            
        return redirect('assignment_detail', course_slug=course_slug, assignment_id=submission.assignment.id)
    
    context = {
        'course': course,
        'submission': submission,
    }
    
    return render(request, 'courses/grade_submission.html', context)