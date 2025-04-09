from django.urls import path
from . import views

urlpatterns = [
    # Conversations
    path('', views.conversation_list, name='conversation_list'),
    path('create/', views.conversation_create, name='conversation_create'),
    path('<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('<int:pk>/delete/', views.conversation_delete, name='conversation_delete'),
    
    # Messages
    path('<int:conversation_id>/messages/create/', views.message_create, name='message_create'),
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    path('notifications/<int:pk>/delete/', views.notification_delete, name='notification_delete'),
]