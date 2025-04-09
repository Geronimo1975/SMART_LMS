from django import forms
from .models import Conversation, Message

class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['subject']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    # This field is not part of the model
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        required=True,
        help_text='Start the conversation with a message'
    )
    
    # MultipleChoiceField for selecting participants
    participants = forms.ModelMultipleChoiceField(
        queryset=None,  # Set in __init__
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=True,
        help_text='Select one or more participants'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        from django.contrib.auth.models import User
        # Exclude current user from participants
        if user:
            self.fields['participants'].queryset = User.objects.exclude(id=user.id)
        else:
            self.fields['participants'].queryset = User.objects.all()

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'content': 'Message',
        }