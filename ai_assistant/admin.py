from django.contrib import admin
from .models import AIAssistant, AIAssistantConversation, AIAssistantMessage

class AIAssistantMessageInline(admin.TabularInline):
    model = AIAssistantMessage
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('message_type', 'content', 'timestamp')

@admin.register(AIAssistant)
class AIAssistantAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'voice', 'is_active', 'created_at')
    list_filter = ('is_active', 'voice', 'created_at')
    search_fields = ('name', 'course__title', 'greeting_message')
    readonly_fields = ('created_at', 'updated_at', 'retell_agent_id')
    fieldsets = (
        (None, {
            'fields': ('name', 'course', 'is_active')
        }),
        ('Voice Configuration', {
            'fields': ('voice', 'greeting_message')
        }),
        ('RetellAI Integration', {
            'fields': ('retell_agent_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AIAssistantConversation)
class AIAssistantConversationAdmin(admin.ModelAdmin):
    list_display = ('assistant', 'user', 'session_id', 'started_at', 'ended_at')
    list_filter = ('started_at', 'ended_at', 'assistant')
    search_fields = ('session_id', 'user__username', 'assistant__name')
    readonly_fields = ('started_at',)
    inlines = [AIAssistantMessageInline]

@admin.register(AIAssistantMessage)
class AIAssistantMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'message_type', 'content_preview', 'timestamp')
    list_filter = ('message_type', 'timestamp', 'conversation__assistant')
    search_fields = ('content', 'conversation__session_id')
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'
