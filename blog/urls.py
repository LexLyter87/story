from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.StoryListView.as_view(), name='story_list'),
    path('story/<str:slug>/', views.StoryDetailView.as_view(), name='story_detail'),
    path('create/', views.StoryCreateView.as_view(), name='story_create'),
    path('story/<str:slug>/edit/', views.StoryUpdateView.as_view(), name='story_update'),
    path('story/<str:slug>/delete/', views.StoryDeleteView.as_view(), name='story_delete'),
    path('story/<str:slug>/comment/', views.add_comment, name='add_comment'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('author/<str:username>/', views.UserStoryListView.as_view(), name='user_stories'),
    path('category/<str:slug>/', views.CategoryStoryListView.as_view(), name='category_stories'),
    path('story/<str:slug>/like/', views.toggle_like, name='story_like'),
]
