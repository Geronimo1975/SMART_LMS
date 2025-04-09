from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Conversation(models.Model):
    """
    A conversation between two or more users.
    """
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation: {self.subject or 'No subject'}"
    
    def get_absolute_url(self):
        return reverse('conversation_detail', kwargs={'pk': self.pk})
    
    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()
    
    def unread_count(self, user):
        """Count of unread messages for a specific user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()
    
    def other_participants(self, user):
        """Get other participants in the conversation"""
        return self.participants.exclude(id=user.id)

class Message(models.Model):
    """
    A message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

class Notification(models.Model):
    """
    Notification for a user.
    """
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('forum_post', 'New Forum Post'),
        ('forum_topic', 'New Forum Topic'),
        ('forum_reply', 'Reply to Your Post'),
        ('course', 'Course Update'),
        ('assignment', 'Assignment Update'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    related_link = models.URLField(blank=True, null=True)
    
    # Optional relations to specific objects
    related_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    related_forum_post = models.ForeignKey('forums.Post', on_delete=models.SET_NULL, null=True, blank=True)
    related_forum_topic = models.ForeignKey('forums.Topic', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()
    
    @classmethod
    def create_message_notification(cls, user, message):
        sender_name = message.sender.get_full_name() or message.sender.username
        notification = cls.objects.create(
            user=user,
            notification_type='message',
            title=f"New message from {sender_name}",
            message=message.content[:100] + ('...' if len(message.content) > 100 else ''),
            related_message=message,
            related_link=reverse('conversation_detail', kwargs={'pk': message.conversation.pk})
        )
        return notification
    
    @classmethod
    def create_forum_post_notification(cls, user, post):
        sender_name = post.created_by.get_full_name() or post.created_by.username
        notification = cls.objects.create(
            user=user,
            notification_type='forum_post',
            title=f"New post in {post.topic.title}",
            message=post.content[:100] + ('...' if len(post.content) > 100 else ''),
            related_forum_post=post,
            related_link=post.get_absolute_url()
        )
        return notification
