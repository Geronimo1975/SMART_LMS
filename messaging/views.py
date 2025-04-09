from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.models import User

from .models import Conversation, Message, Notification
from .forms import ConversationForm, MessageForm

@login_required
def conversation_list(request):
    """List all conversations for the current user."""
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'messaging/conversation_list.html', context)

@login_required
def conversation_create(request):
    """Create a new conversation."""
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.save()
            
            # Add the current user as a participant
            conversation.participants.add(request.user)
            
            # Add the selected participants
            for user_id in request.POST.getlist('participants'):
                user = User.objects.get(id=user_id)
                conversation.participants.add(user)
            
            # Create the initial message
            if request.POST.get('message'):
                Message.objects.create(
                    conversation=conversation,
                    sender=request.user,
                    content=request.POST.get('message')
                )
                
                # Notify other participants
                for participant in conversation.participants.exclude(id=request.user.id):
                    Notification.objects.create(
                        user=participant,
                        notification_type='message',
                        title=f'New conversation from {request.user.username}',
                        message=f'{request.user.username} has started a conversation with you: {conversation.subject}',
                        related_message=conversation.messages.latest('created_at') if conversation.messages.exists() else None
                    )
                
            messages.success(request, "Conversation started successfully.")
            return redirect('conversation_detail', pk=conversation.id)
    else:
        form = ConversationForm()
        users = User.objects.exclude(id=request.user.id)
        
        # Instructors for courses the user is enrolled in
        enrolled_courses = request.user.courses_enrolled.all()
        instructors = User.objects.filter(courses_teaching__in=enrolled_courses).distinct()
        
        # Students for courses the user is teaching
        teaching_courses = request.user.courses_teaching.all()
        students = User.objects.filter(courses_enrolled__in=teaching_courses).distinct()
        
        # Combine and remove duplicates
        relevant_users = (instructors | students).distinct()
        
    context = {
        'form': form,
        'users': users,
        'relevant_users': relevant_users,
    }
    return render(request, 'messaging/conversation_form.html', context)

@login_required
def conversation_detail(request, pk):
    """View a conversation and its messages."""
    conversation = get_object_or_404(Conversation, pk=pk)
    
    # Check if user is a participant
    if request.user not in conversation.participants.all():
        messages.error(request, "You do not have access to this conversation.")
        return redirect('conversation_list')
    
    # Get all messages for this conversation
    message_list = conversation.messages.order_by('created_at')
    
    # Mark all messages as read for this user
    Message.objects.filter(
        conversation=conversation
    ).exclude(
        sender=request.user
    ).update(is_read=True)
    
    # Mark related notifications as read
    Notification.objects.filter(
        user=request.user, 
        notification_type='message',
        related_message__conversation=conversation
    ).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Update conversation timestamp
            conversation.updated_at = message.created_at
            conversation.save()
            
            # Notify other participants
            for participant in conversation.participants.exclude(id=request.user.id):
                Notification.objects.create(
                    user=participant,
                    notification_type='message',
                    title=f'New message from {request.user.username}',
                    message=f'{request.user.username} has sent you a message in {conversation.subject}',
                    related_message=message
                )
            
            messages.success(request, "Message sent.")
            return redirect('conversation_detail', pk=conversation.id)
    else:
        form = MessageForm()
    
    context = {
        'conversation': conversation,
        'messages': message_list,
        'form': form,
    }
    return render(request, 'messaging/conversation_detail.html', context)

@login_required
def conversation_delete(request, pk):
    """Delete a conversation."""
    conversation = get_object_or_404(Conversation, pk=pk)
    
    # Check if user is a participant
    if request.user not in conversation.participants.all():
        messages.error(request, "You do not have access to this conversation.")
        return redirect('conversation_list')
    
    if request.method == 'POST':
        # Remove user from participants
        conversation.participants.remove(request.user)
        
        # If no participants left, delete the conversation
        if conversation.participants.count() == 0:
            conversation.delete()
            messages.success(request, "Conversation deleted successfully.")
        else:
            messages.success(request, "You have left the conversation.")
            
        return redirect('conversation_list')
    
    context = {
        'conversation': conversation,
    }
    return render(request, 'messaging/conversation_confirm_delete.html', context)

@login_required
def message_create(request, conversation_id):
    """Create a new message in a conversation via AJAX."""
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    
    # Check if user is a participant
    if request.user not in conversation.participants.all():
        return JsonResponse({'status': 'error', 'message': 'Access denied'})
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content = request.POST.get('content')
        
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Update conversation timestamp
            conversation.updated_at = message.created_at
            conversation.save()
            
            # Notify other participants
            for participant in conversation.participants.exclude(id=request.user.id):
                Notification.objects.create(
                    user=participant,
                    notification_type='message',
                    title=f'New message from {request.user.username}',
                    message=f'{request.user.username} has sent you a message in {conversation.subject}',
                    related_message=message
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Message sent',
                'content': message.content,
                'sender': message.sender.username,
                'time': message.created_at.strftime('%H:%M %p'),
                'date': message.created_at.strftime('%b %d, %Y'),
            })
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def message_delete(request, pk):
    """Delete a message."""
    message = get_object_or_404(Message, pk=pk)
    conversation = message.conversation
    
    # Check if user is sender or admin
    if message.sender != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to delete this message.")
        return redirect('conversation_detail', pk=conversation.id)
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, "Message deleted successfully.")
        return redirect('conversation_detail', pk=conversation.id)
    
    context = {
        'message': message,
        'conversation': conversation,
    }
    return render(request, 'messaging/message_confirm_delete.html', context)

@login_required
def notification_list(request):
    """List all notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'messaging/notification_list.html', context)

@login_required
def notification_mark_read(request, pk):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.notification_type == 'message' and notification.related_message:
        return redirect('conversation_detail', pk=notification.related_message.conversation.id)
    elif notification.notification_type == 'forum_post' and notification.related_forum_post:
        return redirect('topic_detail', 
                        forum_slug=notification.related_forum_post.topic.forum.slug, 
                        slug=notification.related_forum_post.topic.slug)
    else:
        return redirect('notification_list')

@login_required
def notification_mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notification_list')

@login_required
def notification_delete(request, pk):
    """Delete a notification."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    if request.method == 'POST':
        notification.delete()
        messages.success(request, "Notification deleted successfully.")
        return redirect('notification_list')
    
    context = {
        'notification': notification,
    }
    return render(request, 'messaging/notification_confirm_delete.html', context)
