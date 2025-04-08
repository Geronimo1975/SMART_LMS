from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Avg, Count, Sum
from .models import Course, Assignment, Submission, Material, Enrollment, Grade
from .forms import (CourseForm, AssignmentForm, MaterialForm, 
                   SubmissionForm, EnrollStudentForm, GradeSubmissionForm)
from accounts.models import User

# Helper functions
def is_teacher(user):
    return user.role == User.TEACHER

def is_student(user):
    return user.role == User.STUDENT

def can_edit_course(user, course):
    return is_teacher(user) and user == course.teacher

# Course views
@login_required
def course_list(request):
    if is_teacher(request.user):
        # Teachers see courses they teach
        courses = Course.objects.filter(teacher=request.user)
    else:
        # Students see courses they're enrolled in
        enrollments = Enrollment.objects.filter(student=request.user, is_active=True)
        courses = Course.objects.filter(enrollments__in=enrollments)
    
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    # Check if the user has access to this course
    if is_teacher(request.user):
        if request.user != course.teacher:
            return HttpResponseForbidden("You don't have permission to view this course.")
    else:
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
            if not enrollment.is_active:
                return HttpResponseForbidden("You're not currently enrolled in this course.")
        except Enrollment.DoesNotExist:
            return HttpResponseForbidden("You're not enrolled in this course.")
    
    # Get assignments and materials for this course
    assignments = Assignment.objects.filter(course=course)
    materials = Material.objects.filter(course=course)
    
    # If student, get their submissions
    if is_student(request.user):
        submissions = Submission.objects.filter(
            assignment__course=course, 
            student=request.user
        )
        # Create a dict mapping assignment IDs to submissions
        submission_map = {sub.assignment_id: sub for sub in submissions}
    else:
        submission_map = {}
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'assignments': assignments,
        'materials': materials,
        'submission_map': submission_map,
    })

@login_required
def course_create(request):
    if not is_teacher(request.user):
        messages.error(request, "Only teachers can create courses.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, f"Course '{course.title}' has been created.")
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm()
    
    return render(request, 'courses/course_create.html', {'form': form})

@login_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to edit this course.")
        return redirect('course_detail', pk=course.pk)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' has been updated.")
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/course_edit.html', {'form': form, 'course': course})

@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to delete this course.")
        return redirect('course_detail', pk=course.pk)
    
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f"Course '{course_title}' has been deleted.")
        return redirect('course_list')
    
    return render(request, 'courses/course_delete.html', {'course': course})

# Assignment views
@login_required
def assignment_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to add assignments to this course.")
        return redirect('course_detail', pk=course.pk)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, f"Assignment '{assignment.title}' has been created.")
            return redirect('course_detail', pk=course.pk)
    else:
        form = AssignmentForm()
    
    return render(request, 'courses/assignment_create.html', {
        'form': form, 
        'course': course
    })

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    course = assignment.course
    
    # Check if the user has access to this assignment
    if is_teacher(request.user):
        if request.user != course.teacher:
            return HttpResponseForbidden("You don't have permission to view this assignment.")
        
        # Teachers see all submissions
        submissions = Submission.objects.filter(assignment=assignment)
    else:
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
            if not enrollment.is_active:
                return HttpResponseForbidden("You're not currently enrolled in this course.")
        except Enrollment.DoesNotExist:
            return HttpResponseForbidden("You're not enrolled in this course.")
        
        # Students only see their own submission
        submissions = Submission.objects.filter(
            assignment=assignment, 
            student=request.user
        )
    
    return render(request, 'courses/assignment_detail.html', {
        'assignment': assignment,
        'course': course,
        'submissions': submissions,
    })

@login_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    course = assignment.course
    
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to edit this assignment.")
        return redirect('assignment_detail', pk=assignment.pk)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Assignment '{assignment.title}' has been updated.")
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm(instance=assignment)
    
    return render(request, 'courses/assignment_edit.html', {
        'form': form, 
        'assignment': assignment,
        'course': course
    })

@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    course = assignment.course
    
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to delete this assignment.")
        return redirect('assignment_detail', pk=assignment.pk)
    
    if request.method == 'POST':
        course_id = course.id
        assignment_title = assignment.title
        assignment.delete()
        messages.success(request, f"Assignment '{assignment_title}' has been deleted.")
        return redirect('course_detail', pk=course_id)
    
    return render(request, 'courses/assignment_delete.html', {
        'assignment': assignment,
        'course': course
    })

# Submission views
@login_required
def submission_create(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    course = assignment.course
    
    # Only students enrolled in the course can submit
    if not is_student(request.user):
        messages.error(request, "Only students can submit assignments.")
        return redirect('assignment_detail', pk=assignment.pk)
    
    try:
        enrollment = Enrollment.objects.get(student=request.user, course=course)
        if not enrollment.is_active:
            messages.error(request, "You're not currently enrolled in this course.")
            return redirect('dashboard')
    except Enrollment.DoesNotExist:
        messages.error(request, "You're not enrolled in this course.")
        return redirect('dashboard')
    
    # Check if a submission already exists
    try:
        submission = Submission.objects.get(assignment=assignment, student=request.user)
        is_update = True
    except Submission.DoesNotExist:
        submission = None
        is_update = False
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            
            # If the assignment is past due, mark as late
            if assignment.is_past_due:
                messages.warning(request, "This assignment is past due. Your submission may be marked as late.")
            
            submission.save()
            
            if is_update:
                messages.success(request, "Your submission has been updated.")
            else:
                messages.success(request, "Your submission has been received.")
            
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = SubmissionForm(instance=submission)
    
    return render(request, 'courses/submission_create.html', {
        'form': form,
        'assignment': assignment,
        'course': course,
        'is_update': is_update
    })

@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    assignment = submission.assignment
    course = assignment.course
    
    # Check if the user can view this submission
    if is_teacher(request.user):
        if request.user != course.teacher:
            return HttpResponseForbidden("You don't have permission to view this submission.")
    elif request.user != submission.student:
        return HttpResponseForbidden("You can only view your own submissions.")
    
    # Get the grade if it exists
    try:
        grade = Grade.objects.get(submission=submission)
    except Grade.DoesNotExist:
        grade = None
    
    return render(request, 'courses/submission_detail.html', {
        'submission': submission,
        'assignment': assignment,
        'course': course,
        'grade': grade
    })

# Material views
@login_required
def material_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to add materials to this course.")
        return redirect('course_detail', pk=course.pk)
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, f"Material '{material.title}' has been added.")
            return redirect('course_detail', pk=course.pk)
    else:
        form = MaterialForm()
    
    return render(request, 'courses/material_upload.html', {
        'form': form,
        'course': course
    })

@login_required
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    course = material.course
    
    # Check if the user has access to this material
    if is_teacher(request.user):
        if request.user != course.teacher:
            return HttpResponseForbidden("You don't have permission to view this material.")
    else:
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
            if not enrollment.is_active:
                return HttpResponseForbidden("You're not currently enrolled in this course.")
        except Enrollment.DoesNotExist:
            return HttpResponseForbidden("You're not enrolled in this course.")
    
    return render(request, 'courses/material_detail.html', {
        'material': material,
        'course': course
    })

@login_required
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    course = material.course
    
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to edit this material.")
        return redirect('material_detail', pk=material.pk)
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, f"Material '{material.title}' has been updated.")
            return redirect('material_detail', pk=material.pk)
    else:
        form = MaterialForm(instance=material)
    
    return render(request, 'courses/material_edit.html', {
        'form': form,
        'material': material,
        'course': course
    })

@login_required
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    course = material.course
    
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to delete this material.")
        return redirect('material_detail', pk=material.pk)
    
    if request.method == 'POST':
        course_id = course.id
        material_title = material.title
        material.delete()
        messages.success(request, f"Material '{material_title}' has been deleted.")
        return redirect('course_detail', pk=course_id)
    
    return render(request, 'courses/material_delete.html', {
        'material': material,
        'course': course
    })

# Enrollment views
@login_required
def enroll_in_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if not is_student(request.user):
        messages.error(request, "Only students can enroll in courses.")
        return redirect('dashboard')
    
    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'is_active': True}
    )
    
    if created:
        messages.success(request, f"You have successfully enrolled in {course.title}.")
    else:
        if not enrollment.is_active:
            enrollment.is_active = True
            enrollment.save()
            messages.success(request, f"Your enrollment in {course.title} has been reactivated.")
        else:
            messages.info(request, f"You are already enrolled in {course.title}.")
    
    return redirect('course_detail', pk=course.pk)

@login_required
def unenroll_from_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if not is_student(request.user):
        messages.error(request, "Only students can unenroll from courses.")
        return redirect('dashboard')
    
    try:
        enrollment = Enrollment.objects.get(student=request.user, course=course)
        enrollment.is_active = False
        enrollment.save()
        messages.success(request, f"You have successfully unenrolled from {course.title}.")
    except Enrollment.DoesNotExist:
        messages.error(request, "You are not enrolled in this course.")
    
    return redirect('dashboard')

@login_required
def manage_students(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    
    if not can_edit_course(request.user, course):
        messages.error(request, "You don't have permission to manage students for this course.")
        return redirect('course_detail', pk=course.pk)
    
    # Get all enrollments for this course
    enrollments = Enrollment.objects.filter(course=course)
    
    # Handle adding a new student
    if request.method == 'POST':
        form = EnrollStudentForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            
            # Check if already enrolled
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={'is_active': True}
            )
            
            if created:
                messages.success(request, f"{student.username} has been enrolled in this course.")
            else:
                if not enrollment.is_active:
                    enrollment.is_active = True
                    enrollment.save()
                    messages.success(request, f"{student.username}'s enrollment has been reactivated.")
                else:
                    messages.info(request, f"{student.username} is already enrolled in this course.")
            
            return redirect('manage_students', course_id=course.pk)
    else:
        form = EnrollStudentForm()
    
    return render(request, 'courses/manage_students.html', {
        'course': course,
        'enrollments': enrollments,
        'form': form
    })

# Grading views
@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    assignment = submission.assignment
    course = assignment.course
    
    if not is_teacher(request.user) or request.user != course.teacher:
        return HttpResponseForbidden("You don't have permission to grade this submission.")
    
    # Check if a grade already exists
    try:
        grade = Grade.objects.get(submission=submission)
    except Grade.DoesNotExist:
        grade = None
    
    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=grade, assignment=assignment)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.assignment = assignment
            grade.student = submission.student
            grade.submission = submission
            grade.graded_by = request.user
            grade.save()
            
            # Mark submission as graded
            submission.is_graded = True
            submission.save()
            
            messages.success(request, f"Submission has been graded with {grade.points} points.")
            return redirect('submission_detail', pk=submission.pk)
    else:
        form = GradeSubmissionForm(instance=grade, assignment=assignment)
    
    return render(request, 'courses/grade_submission.html', {
        'form': form,
        'submission': submission,
        'assignment': assignment,
        'course': course
    })
