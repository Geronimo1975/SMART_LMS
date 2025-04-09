import os
import json
import uuid
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RetellAIService:
    """Service for interacting with RetellAI API"""
    
    BASE_URL = "https://api.retellai.com/v1"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('RETELL_API_KEY')
        if not self.api_key:
            raise ValueError("RetellAI API key is required")
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make a request to the RetellAI API"""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, params=params)
            elif method.lower() == 'post':
                response = requests.post(url, headers=headers, json=data)
            elif method.lower() == 'put':
                response = requests.put(url, headers=headers, json=data)
            elif method.lower() == 'delete':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else None
        
        except requests.exceptions.RequestException as e:
            logger.error(f"RetellAI API error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.content}")
            raise
    
    def create_agent(self, name, voice, llm_webhook_url, register_webhook_url=None):
        """Create a new RetellAI agent"""
        data = {
            "name": name,
            "voice": voice,
            "llm_webhook_url": llm_webhook_url,
            "register_webhook_url": register_webhook_url,
            "ambient_sound": "office-ambient",  # Optional ambient sound
            "llm_webhook_auth": {
                "type": "bearer_token",
                "token": f"lms-token-{uuid.uuid4().hex[:10]}"  # Generate a unique token
            }
        }
        
        return self._make_request('post', 'agents', data)
    
    def get_agent(self, agent_id):
        """Get information about a RetellAI agent"""
        return self._make_request('get', f'agents/{agent_id}')
    
    def update_agent(self, agent_id, data):
        """Update a RetellAI agent"""
        return self._make_request('put', f'agents/{agent_id}', data)
    
    def delete_agent(self, agent_id):
        """Delete a RetellAI agent"""
        return self._make_request('delete', f'agents/{agent_id}')
    
    def get_call(self, call_id):
        """Get information about a call"""
        return self._make_request('get', f'calls/{call_id}')
    
    def list_calls(self, agent_id=None, limit=10):
        """List calls for an agent or all calls"""
        params = {'limit': limit}
        if agent_id:
            params['agent_id'] = agent_id
        
        return self._make_request('get', 'calls', params=params)
    
    def end_call(self, call_id):
        """End an active call"""
        return self._make_request('post', f'calls/{call_id}/end')


class CourseAssistantService:
    """Service for handling course assistant AI logic"""
    
    def __init__(self, assistant=None):
        from .models import AIAssistant, AIAssistantConversation, AIAssistantMessage
        self.AIAssistant = AIAssistant
        self.AIAssistantConversation = AIAssistantConversation
        self.AIAssistantMessage = AIAssistantMessage
        self.assistant = assistant
        self.retell_service = RetellAIService()
    
    def create_assistant_for_course(self, course, name=None, voice="nova"):
        """Create an AI assistant for a course"""
        from django.urls import reverse
        from django.conf import settings
        
        # Generate a default name if not provided
        if not name:
            name = f"{course.title} Assistant"
        
        # Base URL for webhooks
        base_url = settings.BASE_URL if hasattr(settings, 'BASE_URL') else 'https://example.com'
        
        # Create a RetellAI agent
        llm_webhook_url = f"{base_url}{reverse('ai_assistant:llm_webhook')}"
        register_webhook_url = f"{base_url}{reverse('ai_assistant:register_webhook')}"
        
        try:
            agent_response = self.retell_service.create_agent(
                name=name,
                voice=voice,
                llm_webhook_url=llm_webhook_url,
                register_webhook_url=register_webhook_url
            )
            
            # Create the assistant in our database
            assistant = self.AIAssistant.objects.create(
                name=name,
                course=course,
                voice=voice,
                retell_agent_id=agent_response.get('id')
            )
            
            return assistant
        
        except Exception as e:
            logger.error(f"Failed to create RetellAI agent: {str(e)}")
            raise
    
    def get_course_context(self, course):
        """Get relevant context data about a course for the AI assistant"""
        context = {
            "course_title": course.title,
            "course_description": course.description,
            "instructor": course.instructor.get_full_name() or course.instructor.username,
            "modules": []
        }
        
        # Add information about modules, contents and assignments
        for module in course.modules.all().order_by('order'):
            module_data = {
                "title": module.title,
                "description": module.description,
                "contents": [],
                "assignments": []
            }
            
            # Add content items
            for content in module.contents.all().order_by('order'):
                content_data = {
                    "title": content.title,
                    "type": "text" if content.content_text else "file" if content.content_file else "url"
                }
                module_data["contents"].append(content_data)
            
            # Add assignments
            for assignment in module.assignments.all():
                assignment_data = {
                    "title": assignment.title,
                    "due_date": assignment.due_date.strftime("%Y-%m-%d %H:%M") if assignment.due_date else "No due date",
                    "points": assignment.points
                }
                module_data["assignments"].append(assignment_data)
            
            context["modules"].append(module_data)
        
        return context
    
    def create_system_prompt(self, course):
        """Create a system prompt for the AI assistant based on course data"""
        course_context = self.get_course_context(course)
        
        # Format the course data as a string
        modules_info = ""
        for i, module in enumerate(course_context["modules"], 1):
            modules_info += f"Module {i}: {module['title']}\n"
            modules_info += f"  Description: {module['description']}\n"
            
            if module["contents"]:
                modules_info += "  Content Items:\n"
                for j, content in enumerate(module["contents"], 1):
                    modules_info += f"    {j}. {content['title']} ({content['type']})\n"
            
            if module["assignments"]:
                modules_info += "  Assignments:\n"
                for j, assignment in enumerate(module["assignments"], 1):
                    modules_info += f"    {j}. {assignment['title']} (Due: {assignment['due_date']}, Points: {assignment['points']})\n"
            
            modules_info += "\n"
        
        # Build the system prompt
        system_prompt = f"""
You are an AI assistant for the course "{course_context['course_title']}" taught by {course_context['instructor']}.
Your role is to help students with questions about the course content, assignments, and due dates.

Here is information about the course:
Description: {course_context['course_description']}

Course Structure:
{modules_info}

Guidelines:
1. Be concise, friendly, and helpful.
2. If asked about assignment deadlines or points, provide the accurate information from the course data.
3. If asked about content not in the course data, politely explain that you can only provide information about this specific course.
4. Direct technical issues or grading questions to the instructor.
5. Maintain a supportive, educational tone throughout conversations.
6. If you need to refer to a file or URL content, mention that the student can access it in the course materials.

Your goal is to enhance the learning experience and provide accurate course information.
"""
        return system_prompt

    def handle_llm_webhook(self, request_data):
        """Handle LLM webhook requests from RetellAI"""
        
        # Extract data from the webhook
        call_id = request_data.get('call_id')
        agent_id = request_data.get('agent_id')
        session_id = request_data.get('session_id')
        message = request_data.get('message', {})
        
        try:
            # Find the corresponding assistant
            assistant = self.AIAssistant.objects.get(retell_agent_id=agent_id)
            
            # Find or create conversation
            conversation, created = self.AIAssistantConversation.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'assistant': assistant,
                    'user': None  # We'll update this with register_webhook
                }
            )
            
            # Record the user's message
            if message.get('role') == 'user':
                self.AIAssistantMessage.objects.create(
                    conversation=conversation,
                    message_type='user',
                    content=message.get('content', '')
                )
            
            # Generate a response
            system_prompt = self.create_system_prompt(assistant.course)
            
            # In a real implementation, you might use an LLM API here
            # For now, we'll create a simple response
            response = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "assistant", "content": self._generate_simple_response(message.get('content', ''))}
                ]
            }
            
            # Record the assistant's response
            self.AIAssistantMessage.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=response['messages'][1]['content']
            )
            
            return response
            
        except self.AIAssistant.DoesNotExist:
            logger.error(f"No assistant found for agent_id: {agent_id}")
            return {"error": "Assistant not found"}
        except Exception as e:
            logger.error(f"Error handling LLM webhook: {str(e)}")
            return {"error": str(e)}
    
    def handle_register_webhook(self, request_data):
        """Handle register webhook requests from RetellAI"""
        
        call_id = request_data.get('call_id')
        agent_id = request_data.get('agent_id')
        session_id = request_data.get('session_id')
        user_id = request_data.get('user_id')
        
        try:
            # Find the corresponding assistant
            assistant = self.AIAssistant.objects.get(retell_agent_id=agent_id)
            
            # Find the User from user_id (would need user mapping logic)
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.error(f"User not found for user_id: {user_id}")
                return {"error": "User not found"}
            
            # Find or create conversation and update user
            conversation, created = self.AIAssistantConversation.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'assistant': assistant,
                    'user': user
                }
            )
            
            if not created:
                conversation.user = user
                conversation.save()
            
            # Log the start of conversation
            self.AIAssistantMessage.objects.create(
                conversation=conversation,
                message_type='system',
                content=f"Conversation started with {assistant.name}"
            )
            
            return {"success": True}
            
        except self.AIAssistant.DoesNotExist:
            logger.error(f"No assistant found for agent_id: {agent_id}")
            return {"error": "Assistant not found"}
        except Exception as e:
            logger.error(f"Error handling register webhook: {str(e)}")
            return {"error": str(e)}
    
    def _generate_simple_response(self, user_message):
        """Generate a simple response for testing purposes"""
        if not user_message:
            return "Hello! I'm your course assistant. How can I help you today?"
        
        user_message = user_message.lower()
        
        if "assignment" in user_message or "homework" in user_message:
            return "Your upcoming assignments can be found in the course modules. Each assignment has details about requirements and due dates. Let me know if you need help with a specific assignment!"
        
        if "deadline" in user_message or "due date" in user_message:
            return "Assignment due dates are listed in each assignment's details. I recommend setting calendar reminders a few days before each deadline to manage your time effectively."
        
        if "module" in user_message or "lecture" in user_message:
            return "The course is divided into several modules, each containing lecture materials, readings, and assignments. You can progress through them at your own pace, but make sure to complete assignments by their due dates."
        
        if "instructor" in user_message or "professor" in user_message or "teacher" in user_message:
            return "Your instructor is available during office hours and via the messaging system. For specific questions about grading or course policies, I recommend contacting them directly."
        
        # Default response
        return "I'm here to help you with any questions about the course. You can ask about assignments, due dates, course materials, or anything else related to the course content."