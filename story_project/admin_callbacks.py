"""Callback функции для Unfold Admin"""
import os
from blog.models import Story, Comment, Like
from django.contrib.auth.models import User


def environment_callback(request):
    """Показывает окружение в админке"""
    env = os.getenv('DJANGO_SETTINGS_MODULE', 'dev')
    if 'prod' in env:
        return ['PRODUCTION', 'danger']
    elif 'dev' in env:
        return ['DEVELOPMENT', 'warning']
    return ['LOCAL', 'info']


def dashboard_callback(request, context):
    """Добавляет статистику на dashboard"""
    context.update({
        "stats": {
            "stories": Story.objects.filter(status=Story.Status.PUBLISHED).count(),
            "drafts": Story.objects.filter(status=Story.Status.DRAFT).count(),
            "comments": Comment.objects.filter(is_active=True).count(),
            "users": User.objects.count(),
            "total_likes": Like.objects.count(),
        }
    })
    return context
