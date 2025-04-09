from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.db.models import Count, Q

from .models import Forum, Topic, Post, Subscription
from messaging.models import Notification
from .forms import ForumForm, TopicForm, PostForm

def forum_list(request):
    """List all forums."""
    forums = Forum.objects.filter(is_active=True)
    
    # Add course-specific forums if user is enrolled or is instructor
    if request.user.is_authenticated:
        # Get courses where user is an instructor
        instructor_courses = request.user.courses_teaching.all()
        
        # Get courses where user is enrolled
        enrolled_courses = request.user.courses_enrolled.all()
        
        # Get course-specific forums for these courses
        course_forums = Forum.objects.filter(
            Q(course__in=instructor_courses) | 
            Q(course__in=enrolled_courses)
        ).distinct()
        
        # Combine querysets
        forums = (forums | course_forums).distinct()
    
    context = {
        'forums': forums,
    }
    return render(request, 'forums/forum_list.html', context)

@login_required
def forum_create(request):
    """Create a new forum."""
    # Only staff can create forums
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to create forums.")
        return redirect('forum_list')
    
    if request.method == 'POST':
        form = ForumForm(request.POST)
        if form.is_valid():
            forum = form.save(commit=False)
            forum.save()
            messages.success(request, f"Forum '{forum.title}' created successfully.")
            return redirect('forum_detail', slug=forum.slug)
    else:
        form = ForumForm()
    
    context = {
        'form': form,
        'title': 'Create Forum',
    }
    return render(request, 'forums/forum_form.html', context)

def forum_detail(request, slug):
    """Display topics in a forum."""
    forum = get_object_or_404(Forum, slug=slug, is_active=True)
    
    # Check if the forum is course-specific and if the user has access
    if forum.course and request.user.is_authenticated:
        is_instructor = request.user == forum.course.instructor
        is_enrolled = request.user in forum.course.students.all()
        if not (is_instructor or is_enrolled or request.user.is_staff):
            messages.error(request, "You don't have access to this forum.")
            return redirect('forum_list')
    
    # Get topics with annotated post counts and last post info
    topics = forum.topics.select_related('created_by').annotate(
        post_count=Count('posts')
    ).order_by('-is_pinned', '-updated_at')
    
    context = {
        'forum': forum,
        'topics': topics,
    }
    return render(request, 'forums/forum_detail.html', context)

@login_required
def forum_edit(request, slug):
    """Edit a forum."""
    forum = get_object_or_404(Forum, slug=slug)
    
    # Only staff can edit forums
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to edit forums.")
        return redirect('forum_detail', slug=forum.slug)
    
    if request.method == 'POST':
        form = ForumForm(request.POST, instance=forum)
        if form.is_valid():
            form.save()
            messages.success(request, f"Forum '{forum.title}' updated successfully.")
            return redirect('forum_detail', slug=forum.slug)
    else:
        form = ForumForm(instance=forum)
    
    context = {
        'form': form,
        'forum': forum,
        'title': 'Edit Forum',
    }
    return render(request, 'forums/forum_form.html', context)

@login_required
def topic_create(request, forum_slug):
    """Create a new topic in a forum."""
    forum = get_object_or_404(Forum, slug=forum_slug, is_active=True)
    
    # Check if the forum is course-specific and if the user has access
    if forum.course:
        is_instructor = request.user == forum.course.instructor
        is_enrolled = request.user in forum.course.students.all()
        if not (is_instructor or is_enrolled or request.user.is_staff):
            messages.error(request, "You don't have access to this forum.")
            return redirect('forum_list')
    
    if request.method == 'POST':
        topic_form = TopicForm(request.POST)
        post_form = PostForm(request.POST)
        
        if topic_form.is_valid() and post_form.is_valid():
            # Create the topic
            topic = topic_form.save(commit=False)
            topic.forum = forum
            topic.created_by = request.user
            topic.save()
            
            # Create the initial post
            post = post_form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            
            # Auto-subscribe the creator
            Subscription.objects.create(user=request.user, topic=topic)
            
            messages.success(request, f"Topic '{topic.title}' created successfully.")
            return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    else:
        topic_form = TopicForm()
        post_form = PostForm()
    
    context = {
        'topic_form': topic_form,
        'post_form': post_form,
        'forum': forum,
        'title': 'Create Topic',
    }
    return render(request, 'forums/topic_form.html', context)

def topic_detail(request, forum_slug, slug):
    """Display posts in a topic."""
    forum = get_object_or_404(Forum, slug=forum_slug, is_active=True)
    topic = get_object_or_404(Topic, forum=forum, slug=slug)
    
    # Check if the forum is course-specific and if the user has access
    if forum.course and request.user.is_authenticated:
        is_instructor = request.user == forum.course.instructor
        is_enrolled = request.user in forum.course.students.all()
        if not (is_instructor or is_enrolled or request.user.is_staff):
            messages.error(request, "You don't have access to this topic.")
            return redirect('forum_list')
    
    # Increment view count
    topic.views += 1
    topic.save()
    
    # Get posts
    posts = topic.posts.select_related('created_by').order_by('created_at')
    
    # Check if user is subscribed
    is_subscribed = False
    can_post = not topic.is_closed
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(user=request.user, topic=topic).exists()
        # Always allow staff and instructors to post in closed topics
        if topic.is_closed and (request.user.is_staff or (forum.course and request.user == forum.course.instructor)):
            can_post = True
    
    context = {
        'forum': forum,
        'topic': topic,
        'posts': posts,
        'is_subscribed': is_subscribed,
        'can_post': can_post,
    }
    return render(request, 'forums/topic_detail.html', context)

@login_required
def topic_edit(request, forum_slug, slug):
    """Edit a topic."""
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, forum=forum, slug=slug)
    
    # Check permissions
    if not (request.user == topic.created_by or request.user.is_staff or 
            (forum.course and request.user == forum.course.instructor)):
        messages.error(request, "You don't have permission to edit this topic.")
        return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, f"Topic '{topic.title}' updated successfully.")
            return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    else:
        form = TopicForm(instance=topic)
    
    context = {
        'form': form,
        'forum': forum,
        'topic': topic,
        'title': 'Edit Topic',
    }
    return render(request, 'forums/topic_edit.html', context)

@login_required
def topic_close(request, forum_slug, slug):
    """Close or reopen a topic."""
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, forum=forum, slug=slug)
    
    # Check permissions
    if not (request.user.is_staff or 
            (forum.course and request.user == forum.course.instructor)):
        messages.error(request, "You don't have permission to close/reopen this topic.")
        return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    
    # Toggle status
    topic.is_closed = not topic.is_closed
    topic.save()
    
    status = "closed" if topic.is_closed else "reopened"
    messages.success(request, f"Topic '{topic.title}' {status} successfully.")
    return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)

@login_required
def topic_pin(request, forum_slug, slug):
    """Pin or unpin a topic."""
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, forum=forum, slug=slug)
    
    # Check permissions
    if not (request.user.is_staff or 
            (forum.course and request.user == forum.course.instructor)):
        messages.error(request, "You don't have permission to pin/unpin this topic.")
        return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    
    # Toggle status
    topic.is_pinned = not topic.is_pinned
    topic.save()
    
    status = "pinned" if topic.is_pinned else "unpinned"
    messages.success(request, f"Topic '{topic.title}' {status} successfully.")
    return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)

@login_required
def topic_subscribe(request, forum_slug, slug):
    """Subscribe to a topic."""
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, forum=forum, slug=slug)
    
    # Check if already subscribed
    subscription, created = Subscription.objects.get_or_create(user=request.user, topic=topic)
    
    if created:
        messages.success(request, f"You have subscribed to '{topic.title}'.")
    else:
        messages.info(request, f"You are already subscribed to '{topic.title}'.")
    
    return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)

@login_required
def topic_unsubscribe(request, forum_slug, slug):
    """Unsubscribe from a topic."""
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, forum=forum, slug=slug)
    
    # Delete subscription if exists
    deleted, _ = Subscription.objects.filter(user=request.user, topic=topic).delete()
    
    if deleted:
        messages.success(request, f"You have unsubscribed from '{topic.title}'.")
    else:
        messages.info(request, f"You were not subscribed to '{topic.title}'.")
    
    return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)

@login_required
def post_create(request, forum_slug, topic_slug):
    """Create a reply in a topic."""
    forum = get_object_or_404(Forum, slug=forum_slug, is_active=True)
    topic = get_object_or_404(Topic, forum=forum, slug=topic_slug)
    
    # Check if the forum is course-specific and if the user has access
    if forum.course:
        is_instructor = request.user == forum.course.instructor
        is_enrolled = request.user in forum.course.students.all()
        if not (is_instructor or is_enrolled or request.user.is_staff):
            messages.error(request, "You don't have access to this topic.")
            return redirect('forum_list')
    
    # Check if topic is closed
    if topic.is_closed and not (request.user.is_staff or 
                               (forum.course and request.user == forum.course.instructor)):
        messages.error(request, "This topic is closed for new replies.")
        return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            
            # Update topic timestamp
            topic.updated_at = post.created_at
            topic.save()
            
            # Notify subscribers
            subscribers = User.objects.filter(
                forum_subscriptions__topic=topic
            ).exclude(id=request.user.id)
            
            for subscriber in subscribers:
                Notification.objects.create(
                    user=subscriber,
                    notification_type='forum_post',
                    title=f'New reply in "{topic.title}"',
                    message=f'{request.user.username} has posted in a topic you are subscribed to: {topic.title}',
                    related_forum_post=post
                )
            
            messages.success(request, "Your reply has been posted.")
            
            # Return to the last page of the topic
            return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    else:
        form = PostForm()
    
    context = {
        'form': form,
        'forum': forum,
        'topic': topic,
        'title': 'Post Reply',
    }
    return render(request, 'forums/post_form.html', context)

@login_required
def post_edit(request, forum_slug, topic_slug, pk):
    """Edit a post."""
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, forum=forum, slug=topic_slug)
    post = get_object_or_404(Post, pk=pk, topic=topic)
    
    # Check permissions
    if not (request.user == post.created_by or request.user.is_staff or 
            (forum.course and request.user == forum.course.instructor)):
        messages.error(request, "You don't have permission to edit this post.")
        return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.is_edited = True
            post.save()
            messages.success(request, "Your post has been updated.")
            return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'forum': forum,
        'topic': topic,
        'post': post,
        'title': 'Edit Post',
    }
    return render(request, 'forums/post_form.html', context)

@login_required
def post_delete(request, forum_slug, topic_slug, pk):
    """Delete a post."""
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, forum=forum, slug=topic_slug)
    post = get_object_or_404(Post, pk=pk, topic=topic)
    
    # Check permissions
    if not (request.user == post.created_by or request.user.is_staff or 
            (forum.course and request.user == forum.course.instructor)):
        messages.error(request, "You don't have permission to delete this post.")
        return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    
    # Don't allow deletion of the first post (would break the topic)
    if post == topic.posts.earliest('created_at'):
        messages.error(request, "Cannot delete the first post of a topic.")
        return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('topic_detail', forum_slug=forum.slug, slug=topic.slug)
    
    context = {
        'forum': forum,
        'topic': topic,
        'post': post,
    }
    return render(request, 'forums/post_confirm_delete.html', context)
