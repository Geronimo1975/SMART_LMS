from django.urls import path
from . import views

urlpatterns = [
    # Forums
    path('', views.forum_list, name='forum_list'),
    path('create/', views.forum_create, name='forum_create'),
    path('<slug:slug>/', views.forum_detail, name='forum_detail'),
    path('<slug:slug>/edit/', views.forum_edit, name='forum_edit'),
    
    # Topics
    path('<slug:forum_slug>/topics/create/', views.topic_create, name='topic_create'),
    path('<slug:forum_slug>/<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('<slug:forum_slug>/<slug:slug>/edit/', views.topic_edit, name='topic_edit'),
    path('<slug:forum_slug>/<slug:slug>/close/', views.topic_close, name='topic_close'),
    path('<slug:forum_slug>/<slug:slug>/pin/', views.topic_pin, name='topic_pin'),
    path('<slug:forum_slug>/<slug:slug>/subscribe/', views.topic_subscribe, name='topic_subscribe'),
    path('<slug:forum_slug>/<slug:slug>/unsubscribe/', views.topic_unsubscribe, name='topic_unsubscribe'),
    
    # Posts
    path('<slug:forum_slug>/<slug:topic_slug>/posts/create/', views.post_create, name='post_create'),
    path('<slug:forum_slug>/<slug:topic_slug>/posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('<slug:forum_slug>/<slug:topic_slug>/posts/<int:pk>/delete/', views.post_delete, name='post_delete'),
]