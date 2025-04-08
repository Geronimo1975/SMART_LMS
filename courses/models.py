from django.db import models
from accounts.models import User
from django.urls import reverse
from django.utils import timezone
import os

def assignment_file_path(instance, filename):
    return os.path.join('assignments', instance.course.code, filename)

def submission_file_path(instance, filename):
    return os.path.join('submissions', instance.assignment.course.code, 
                         instance.assignment.id.__str__(), instance.student.username, filename)

def material_file_path(instance, filename):
    return os.path.join('materials', instance.course.code, filename)

class Course(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_teaching',
                               limit_choices_to={'role': User.TEACHER})
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.code}: {self.title}"
    
    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'pk': self.pk})
    
    @property
    def is_ongoing(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    @property
    def student_count(self):
        return self.enrollments.filter(is_active=True).count()

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to=assignment_file_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField()
    total_points = models.PositiveIntegerField(default=100)
    
    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.title} - {self.course.code}"
    
    def get_absolute_url(self):
        return reverse('assignment_detail', kwargs={'pk': self.pk})
    
    @property
    def is_past_due(self):
        return timezone.now() > self.due_date

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions',
                               limit_choices_to={'role': User.STUDENT})
    file = models.FileField(upload_to=submission_file_path, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_graded = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.username}'s submission for {self.assignment.title}"
    
    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date
    
    def get_grade(self):
        try:
            return self.grade
        except Grade.DoesNotExist:
            return None

class Material(models.Model):
    FILE = 'file'
    LINK = 'link'
    TEXT = 'text'
    
    MATERIAL_TYPES = [
        (FILE, 'File'),
        (LINK, 'External Link'),
        (TEXT, 'Text Content'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPES, default=FILE)
    file = models.FileField(upload_to=material_file_path, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.course.code}"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments',
                               limit_choices_to={'role': User.STUDENT})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.code}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades',
                               limit_choices_to={'role': User.STUDENT})
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='grades')
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='grade')
    points = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades_given',
                                 limit_choices_to={'role': User.TEACHER})
    graded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'assignment')
    
    def __str__(self):
        return f"{self.student.username}'s grade for {self.assignment.title}: {self.points}/{self.assignment.total_points}"
    
    def save(self, *args, **kwargs):
        # Mark the submission as graded
        self.submission.is_graded = True
        self.submission.save()
        super().save(*args, **kwargs)
