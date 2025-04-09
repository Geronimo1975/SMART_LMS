from django.db import models
from django.contrib.auth.models import User
from courses.models import Course

class AIAssistant(models.Model):
    """AI Voice Assistant configuration for courses"""
    
    VOICE_CHOICES = (
        ('alloy', 'Alloy - Neutral, professional, versatile'),
        ('shimmer', 'Shimmer - Warm, welcoming, clear'),
        ('nova', 'Nova - Confident, nurturing, thoughtful'),
        ('echo', 'Echo - Warm, resonant, confident'),
        ('fable', 'Fable - Deep, authoritative, wise'),
        ('onyx', 'Onyx - Smooth, confident, professional'),
    )
    
    name = models.CharField(max_length=100, help_text="Name of the AI assistant")
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='ai_assistant')
    is_active = models.BooleanField(default=True)
    voice = models.CharField(max_length=20, choices=VOICE_CHOICES, default='nova')
    greeting_message = models.TextField(help_text="Message to greet students when they first connect", 
                                        default="Hello! I'm your course assistant. How can I help you today?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # RetellAI specific fields
    retell_agent_id = models.CharField(max_length=255, blank=True, null=True, 
                                     help_text="RetellAI agent ID for this assistant")
    
    def __str__(self):
        return f"{self.name} - {self.course.title}"

class AIAssistantConversation(models.Model):
    """Record of conversations with the AI assistant"""
    assistant = models.ForeignKey(AIAssistant, on_delete=models.CASCADE, related_name='conversations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    session_id = models.CharField(max_length=255, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Conversation {self.session_id} - {self.user.username} with {self.assistant.name}"

class AIAssistantMessage(models.Model):
    """Individual messages in a conversation with the AI assistant"""
    MESSAGE_TYPES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )
    
    conversation = models.ForeignKey(AIAssistantConversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."
