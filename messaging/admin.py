from django.contrib import admin
from .models import Conversation, Message, Notification

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('sender', 'content', 'is_read', 'created_at')
    raw_id_fields = ('sender',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'created_at', 'updated_at', 'get_participants')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('subject', 'participants__username')
    date_hierarchy = 'created_at'
    filter_horizontal = ('participants',)
    inlines = [MessageInline]

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'content_preview', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__username')
    date_hierarchy = 'created_at'
    raw_id_fields = ('sender', 'conversation')

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Content'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'related_message', 'related_forum_post', 'related_forum_topic')
