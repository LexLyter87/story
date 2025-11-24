from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Story, Category, Comment, Like, UserProfile


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'story_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    @display(description='Количество рассказов', ordering='story_count')
    def story_count(self, obj):
        return obj.stories.count()


@admin.register(Story)
class StoryAdmin(ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'published_at', 'like_count']
    list_filter = ['status', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    list_per_page = 20
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Содержание', {
            'fields': ('content', 'excerpt', 'cover_image')
        }),
        ('Даты', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
    )
    
    @display(description='Лайков', ordering='like_count')
    def like_count(self, obj):
        return obj.likes.count()


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['short_content', 'author', 'story', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['content', 'author__username', 'story__title']
    date_hierarchy = 'created_at'
    list_per_page = 30
    
    actions = ['approve_comments', 'reject_comments']
    
    @display(description='Комментарий')
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    @admin.action(description='Одобрить выбранные комментарии')
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} комментариев одобрено.')
    
    @admin.action(description='Отклонить выбранные комментарии')
    def reject_comments(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} комментариев отклонено.')


@admin.register(Like)
class LikeAdmin(ModelAdmin):
    list_display = ['user', 'story', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'story__title']
    date_hierarchy = 'created_at'


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ['user', 'get_email', 'get_stories_count']
    search_fields = ['user__username', 'user__email', 'bio']
    
    @display(description='Email')
    def get_email(self, obj):
        return obj.user.email
    
    @display(description='Рассказов', ordering='stories_count')
    def get_stories_count(self, obj):
        return obj.user.stories.count()
