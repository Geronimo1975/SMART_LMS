from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging

from courses.models import Course
from .models import AIAssistant, AIAssistantConversation, AIAssistantMessage
from .forms import AIAssistantForm
from .services import RetellAIService, CourseAssistantService

logger = logging.getLogger(__name__)

@login_required
def assistant_list(request):
    """List AI assistants for courses the user is enrolled in or teaching"""
    
    # For instructors, show assistants for their courses
    if hasattr(request.user, 'courses_teaching'):
        teaching_courses = request.user.courses_teaching.all()
        teaching_assistants = AIAssistant.objects.filter(course__in=teaching_courses)
    else:
        teaching_assistants = AIAssistant.objects.none()
    
    # For students, show assistants for enrolled courses
    if hasattr(request.user, 'courses_enrolled'):
        enrolled_courses = request.user.courses_enrolled.all()
        enrolled_assistants = AIAssistant.objects.filter(course__in=enrolled_courses, is_active=True)
    else:
        enrolled_assistants = AIAssistant.objects.none()
    
    context = {
        'teaching_assistants': teaching_assistants,
        'enrolled_assistants': enrolled_assistants,
    }
    return render(request, 'ai_assistant/assistant_list.html', context)

@login_required
def assistant_create(request, course_id=None):
    """Create a new AI assistant for a course"""
    
    # Only instructors can create assistants
    if not hasattr(request.user, 'courses_teaching') or not request.user.courses_teaching.exists():
        messages.error(request, "Only instructors can create AI assistants.")
        return redirect('ai_assistant:assistant_list')
    
    # If course_id provided, pre-select that course
    initial = {}
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        # Verify the user is the instructor for this course
        if course.instructor != request.user:
            messages.error(request, "You can only create assistants for courses you teach.")
            return redirect('ai_assistant:assistant_list')
        initial['course'] = course
    
    if request.method == 'POST':
        form = AIAssistantForm(request.POST)
        if form.is_valid():
            # Verify the user is the instructor for this course
            course = form.cleaned_data['course']
            if course.instructor != request.user:
                messages.error(request, "You can only create assistants for courses you teach.")
                return redirect('ai_assistant:assistant_list')
            
            assistant = form.save(commit=False)
            
            # Create the RetellAI agent
            try:
                service = CourseAssistantService()
                assistant = service.create_assistant_for_course(
                    course=course,
                    name=assistant.name,
                    voice=assistant.voice
                )
                messages.success(request, f"AI assistant '{assistant.name}' created successfully.")
                return redirect('ai_assistant:assistant_detail', assistant_id=assistant.id)
            except Exception as e:
                logger.error(f"Failed to create assistant: {str(e)}")
                messages.error(request, f"Failed to create assistant: {str(e)}")
                return redirect('ai_assistant:assistant_list')
    else:
        form = AIAssistantForm(initial=initial)
        # Filter courses to only those taught by the user
        form.fields['course'].queryset = request.user.courses_teaching.all()
    
    context = {
        'form': form,
        'title': 'Create AI Assistant',
    }
    return render(request, 'ai_assistant/assistant_form.html', context)

@login_required
def assistant_detail(request, assistant_id):
    """View details of an AI assistant"""
    assistant = get_object_or_404(AIAssistant, id=assistant_id)
    
    # Check if user has access to this assistant
    if assistant.course.instructor != request.user and request.user not in assistant.course.students.all():
        messages.error(request, "You don't have access to this assistant.")
        return redirect('ai_assistant:assistant_list')
    
    # Get conversations for this assistant involving this user
    conversations = AIAssistantConversation.objects.filter(
        assistant=assistant,
        user=request.user
    ).order_by('-started_at')
    
    context = {
        'assistant': assistant,
        'conversations': conversations,
        'is_instructor': assistant.course.instructor == request.user,
    }
    return render(request, 'ai_assistant/assistant_detail.html', context)

@login_required
def assistant_edit(request, assistant_id):
    """Edit an existing AI assistant"""
    assistant = get_object_or_404(AIAssistant, id=assistant_id)
    
    # Only the instructor can edit
    if assistant.course.instructor != request.user:
        messages.error(request, "Only the course instructor can edit assistants.")
        return redirect('ai_assistant:assistant_detail', assistant_id=assistant.id)
    
    if request.method == 'POST':
        form = AIAssistantForm(request.POST, instance=assistant)
        if form.is_valid():
            # Verify the user is still the instructor for this course
            course = form.cleaned_data['course']
            if course.instructor != request.user:
                messages.error(request, "You can only edit assistants for courses you teach.")
                return redirect('ai_assistant:assistant_list')
            
            # Update the AI assistant in our database
            updated_assistant = form.save()
            
            # Update the RetellAI agent if needed
            try:
                retell_service = RetellAIService()
                retell_service.update_agent(
                    agent_id=assistant.retell_agent_id,
                    data={
                        'name': updated_assistant.name,
                        'voice': updated_assistant.voice,
                    }
                )
                messages.success(request, f"AI assistant '{updated_assistant.name}' updated successfully.")
            except Exception as e:
                logger.error(f"Failed to update RetellAI agent: {str(e)}")
                messages.warning(request, f"Assistant updated in database but RetellAI synchronization failed: {str(e)}")
            
            return redirect('ai_assistant:assistant_detail', assistant_id=assistant.id)
    else:
        form = AIAssistantForm(instance=assistant)
        # Filter courses to only those taught by the user
        form.fields['course'].queryset = request.user.courses_teaching.all()
    
    context = {
        'form': form,
        'assistant': assistant,
        'title': 'Edit AI Assistant',
    }
    return render(request, 'ai_assistant/assistant_form.html', context)

@login_required
def assistant_delete(request, assistant_id):
    """Delete an AI assistant"""
    assistant = get_object_or_404(AIAssistant, id=assistant_id)
    
    # Only the instructor can delete
    if assistant.course.instructor != request.user:
        messages.error(request, "Only the course instructor can delete assistants.")
        return redirect('ai_assistant:assistant_detail', assistant_id=assistant.id)
    
    if request.method == 'POST':
        # Delete the RetellAI agent
        try:
            if assistant.retell_agent_id:
                retell_service = RetellAIService()
                retell_service.delete_agent(assistant.retell_agent_id)
        except Exception as e:
            logger.error(f"Failed to delete RetellAI agent: {str(e)}")
            messages.warning(request, f"RetellAI agent deletion failed, but assistant will be removed from database: {str(e)}")
        
        # Delete from our database
        assistant_name = assistant.name
        assistant.delete()
        messages.success(request, f"AI assistant '{assistant_name}' deleted successfully.")
        return redirect('ai_assistant:assistant_list')
    
    context = {
        'assistant': assistant,
    }
    return render(request, 'ai_assistant/assistant_confirm_delete.html', context)

@login_required
def conversation_detail(request, conversation_id):
    """View details of a conversation"""
    conversation = get_object_or_404(AIAssistantConversation, id=conversation_id)
    
    # Check if user has access to this conversation
    if conversation.user != request.user and conversation.assistant.course.instructor != request.user:
        messages.error(request, "You don't have access to this conversation.")
        return redirect('ai_assistant:assistant_list')
    
    messages_list = conversation.messages.order_by('timestamp')
    
    context = {
        'conversation': conversation,
        'messages': messages_list,
        'assistant': conversation.assistant,
        'is_instructor': conversation.assistant.course.instructor == request.user,
    }
    return render(request, 'ai_assistant/conversation_detail.html', context)

@csrf_exempt
@require_POST
def llm_webhook(request):
    """Webhook for RetellAI LLM requests"""
    try:
        # Parse the webhook payload
        data = json.loads(request.body)
        logger.info(f"Received LLM webhook: {data}")
        
        # Handle the webhook with our service
        service = CourseAssistantService()
        response = service.handle_llm_webhook(data)
        
        return JsonResponse(response)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook request")
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_POST
def register_webhook(request):
    """Webhook for RetellAI call registration"""
    try:
        # Parse the webhook payload
        data = json.loads(request.body)
        logger.info(f"Received register webhook: {data}")
        
        # Handle the webhook with our service
        service = CourseAssistantService()
        response = service.handle_register_webhook(data)
        
        return JsonResponse(response)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook request")
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def start_call(request, assistant_id):
    """Generate RetellAI call information for the client"""
    assistant = get_object_or_404(AIAssistant, id=assistant_id)
    
    # Check if user has access to this assistant
    if assistant.course.instructor != request.user and request.user not in assistant.course.students.all():
        messages.error(request, "You don't have access to this assistant.")
        return redirect('ai_assistant:assistant_list')
    
    # In a real implementation, you'd generate a token for the RetellAI client
    # For now, we'll return a placeholder
    call_data = {
        'assistant_id': assistant.id,
        'assistant_name': assistant.name,
        'retell_agent_id': assistant.retell_agent_id,
        'user_id': request.user.id,
        'api_key': "YOUR_RETELL_PUBLIC_API_KEY"  # This would be a public key, not the secret key
    }
    
    return JsonResponse(call_data)
