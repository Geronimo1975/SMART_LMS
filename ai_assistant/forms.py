from django import forms
from .models import AIAssistant

class AIAssistantForm(forms.ModelForm):
    """Form for creating and updating AI assistants"""
    
    class Meta:
        model = AIAssistant
        fields = ['name', 'course', 'voice', 'greeting_message', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'voice': forms.Select(attrs={'class': 'form-select'}),
            'greeting_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'name': 'Name of the AI assistant (e.g., "Course Helper", "Math Tutor")',
            'voice': 'Select the voice personality for your assistant',
            'greeting_message': 'The first message the assistant will say when a student connects',
        }