from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    # Assistant management
    path('', views.assistant_list, name='assistant_list'),
    path('create/', views.assistant_create, name='assistant_create'),
    path('create/<int:course_id>/', views.assistant_create, name='assistant_create_for_course'),
    path('<int:assistant_id>/', views.assistant_detail, name='assistant_detail'),
    path('<int:assistant_id>/edit/', views.assistant_edit, name='assistant_edit'),
    path('<int:assistant_id>/delete/', views.assistant_delete, name='assistant_delete'),
    
    # Conversation views
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    
    # RetellAI integration
    path('webhooks/llm/', views.llm_webhook, name='llm_webhook'),
    path('webhooks/register/', views.register_webhook, name='register_webhook'),
    path('<int:assistant_id>/call/', views.start_call, name='start_call'),
]