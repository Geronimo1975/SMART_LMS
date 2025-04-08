from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
import os

def avatar_upload_path(instance, filename):
    # Get the filename extension
    ext = filename.split('.')[-1]
    # Set the filename as the username
    filename = f"{instance.user.username}.{ext}"
    # Return the upload path
    return os.path.join('avatars', filename)

class User(AbstractUser):
    STUDENT = 'student'
    TEACHER = 'teacher'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (ADMIN, 'Admin'),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    
    def __str__(self):
        return self.username
    
    def is_student(self):
        return self.role == self.STUDENT
    
    def is_teacher(self):
        return self.role == self.TEACHER
    
    def is_admin_user(self):
        return self.role == self.ADMIN

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, default='avatars/default.png')
    
    # Fields specific to teachers
    title = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    office_hours = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_absolute_url(self):
        return reverse('profile_detail', kwargs={'username': self.user.username})
