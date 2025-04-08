from django import forms
from .models import Course, Assignment, Material, Submission, Grade
from accounts.models import User

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'code', 'description', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'total_points', 'file']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'description', 'material_type', 'file', 'link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('material_type')
        file = cleaned_data.get('file')
        link = cleaned_data.get('link')
        
        if material_type == Material.FILE and not file:
            self.add_error('file', 'Please upload a file for file-type material.')
        if material_type == Material.LINK and not link:
            self.add_error('link', 'Please provide a link for link-type material.')
        
        return cleaned_data

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your submission text (if applicable)'}),
        }

class EnrollStudentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.STUDENT),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['points', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, assignment=None, **kwargs):
        super().__init__(*args, **kwargs)
        if assignment:
            self.fields['points'].widget.attrs['max'] = assignment.total_points
            self.fields['points'].widget.attrs['min'] = 0
            self.fields['points'].help_text = f'Max points: {assignment.total_points}'
