from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from courses.models import Course

class Forum(models.Model):
    """
    A forum can be course-specific or general.
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forums', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['title']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum_detail', kwargs={'slug': self.slug})
    
    @property
    def topic_count(self):
        return self.topics.count()
    
    @property
    def post_count(self):
        return sum(topic.post_count for topic in self.topics.all())

class Topic(models.Model):
    """
    A topic belongs to a forum and contains posts.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='topics')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        unique_together = ['forum', 'slug']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('topic_detail', kwargs={'forum_slug': self.forum.slug, 'slug': self.slug})
    
    @property
    def post_count(self):
        return self.posts.count()
    
    @property
    def last_post(self):
        return self.posts.order_by('-created_at').first()

class Post(models.Model):
    """
    A post belongs to a topic.
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"Post by {self.created_by.username} in {self.topic.title}"
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={
            'forum_slug': self.topic.forum.slug,
            'topic_slug': self.topic.slug,
            'pk': self.pk
        })

class Subscription(models.Model):
    """
    Users can subscribe to topics to receive notifications.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_subscriptions')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subscriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'topic']
        
    def __str__(self):
        return f"{self.user.username} subscribed to {self.topic.title}"
