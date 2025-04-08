from django.contrib import admin
from .models import Course, Module, Content, Assignment, Submission

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('students',)


class ContentInline(admin.StackedInline):
    model = Content
    extra = 1


class AssignmentInline(admin.StackedInline):
    model = Assignment
    extra = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description', 'course__title')
    inlines = [ContentInline, AssignmentInline]


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'created_at')
    list_filter = ('module__course', 'created_at')
    search_fields = ('title', 'content_text')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'due_date', 'points')
    list_filter = ('module__course', 'due_date')
    search_fields = ('title', 'description')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'status', 'score')
    list_filter = ('status', 'submitted_at', 'assignment__module__course')
    search_fields = ('student__username', 'assignment__title', 'feedback')