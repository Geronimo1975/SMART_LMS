from django.contrib import admin
from .models import Forum, Topic, Post, Subscription

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'is_active', 'topic_count', 'post_count', 'created_at')
    list_filter = ('is_active', 'course', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'forum', 'created_by', 'created_at', 'views', 'is_pinned', 'is_closed', 'post_count')
    list_filter = ('forum', 'is_pinned', 'is_closed', 'created_at')
    search_fields = ('title', 'created_by__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    raw_id_fields = ('created_by',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('topic', 'created_by', 'created_at', 'is_edited')
    list_filter = ('is_edited', 'created_at', 'topic__forum')
    search_fields = ('content', 'created_by__username', 'topic__title')
    date_hierarchy = 'created_at'
    raw_id_fields = ('created_by', 'topic')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'created_at')
    list_filter = ('created_at', 'topic__forum')
    search_fields = ('user__username', 'topic__title')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'topic')
