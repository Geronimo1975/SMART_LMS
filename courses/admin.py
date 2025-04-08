from django.contrib import admin
from .models import Course, Assignment, Submission, Material, Enrollment, Grade

class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0

class MaterialInline(admin.TabularInline):
    model = Material
    extra = 0

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'teacher', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'teacher')
    search_fields = ('title', 'code', 'description')
    inlines = [AssignmentInline, MaterialInline, EnrollmentInline]

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'total_points')
    list_filter = ('course', 'due_date')
    search_fields = ('title', 'description')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'is_graded')
    list_filter = ('assignment', 'student', 'is_graded')
    search_fields = ('assignment__title', 'student__username')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'material_type', 'uploaded_at')
    list_filter = ('course', 'material_type')
    search_fields = ('title', 'description')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_active')
    list_filter = ('course', 'is_active', 'enrolled_at')
    search_fields = ('student__username', 'course__title')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'points', 'graded_by', 'graded_at')
    list_filter = ('assignment', 'graded_by')
    search_fields = ('student__username', 'assignment__title')
