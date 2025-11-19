from django.contrib import admin
from .models import Category, UserProfile, Story, Comment, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('-status', '-published_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('story', 'author', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('content', 'author__username', 'story__title')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)
    approve_comments.short_description = "Одобрить выбранные комментарии"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('story', 'user', 'created_at')
    search_fields = ('story__title', 'user__username')
    